# Video Streaming Platform - Complete Implementation

## Overview
A comprehensive video streaming platform similar to YouTube, Netflix, or Twitch, designed to handle millions of concurrent users, petabytes of video content, and real-time streaming. This implementation covers video upload, processing, CDN distribution, recommendation systems, and live streaming capabilities.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Video Upload Service](#video-upload-service)
3. [Video Processing Pipeline](#video-processing-pipeline)
4. [Content Delivery Network](#content-delivery-network)
5. [Metadata Management](#metadata-management)
6. [Recommendation Engine](#recommendation-engine)
7. [Live Streaming](#live-streaming)
8. [Analytics and Monitoring](#analytics-and-monitoring)

## System Architecture

### High-Level Architecture

```python
import asyncio
import boto3
import ffmpeg
from typing import Dict, List, Optional, Tuple, AsyncIterator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import uuid
import hashlib
import redis
import logging
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VideoStatus(Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"

class VideoQuality(Enum):
    QUALITY_144P = "144p"
    QUALITY_240P = "240p"
    QUALITY_360P = "360p"
    QUALITY_480P = "480p"
    QUALITY_720P = "720p"
    QUALITY_1080P = "1080p"
    QUALITY_1440P = "1440p"
    QUALITY_2160P = "2160p"

@dataclass
class Video:
    video_id: str
    title: str
    description: str
    uploader_id: str
    duration: int  # seconds
    file_size: int  # bytes
    upload_timestamp: datetime
    status: VideoStatus
    thumbnail_url: str = ""
    tags: List[str] = None
    category: str = ""
    privacy: str = "public"  # public, private, unlisted
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    processed_formats: Dict[str, str] = None  # quality -> url mapping

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.processed_formats is None:
            self.processed_formats = {}

@dataclass
class VideoChunk:
    chunk_id: str
    video_id: str
    quality: VideoQuality
    segment_number: int
    duration: float
    file_path: str
    file_size: int

@dataclass
class LiveStream:
    stream_id: str
    streamer_id: str
    title: str
    description: str
    category: str
    start_time: datetime
    end_time: Optional[datetime] = None
    viewer_count: int = 0
    max_viewers: int = 0
    status: str = "live"  # live, ended, scheduled
    thumbnail_url: str = ""
    stream_key: str = ""

@dataclass
class ViewEvent:
    user_id: str
    video_id: str
    timestamp: datetime
    watch_time: int  # seconds watched
    quality: str
    device_type: str
    location: str
```

## Video Upload Service

### Multi-part Upload Handler

```python
class VideoUploadService:
    def __init__(self, s3_client, database, redis_client, processing_queue):
        self.s3 = s3_client
        self.db = database
        self.redis = redis_client
        self.processing_queue = processing_queue
        self.upload_bucket = "video-uploads"
        self.processed_bucket = "video-processed"

    async def initiate_upload(self, uploader_id: str, video_metadata: Dict) -> Dict:
        """Initiate multipart upload for large video files"""
        video_id = str(uuid.uuid4())

        # Create video record
        video = Video(
            video_id=video_id,
            title=video_metadata['title'],
            description=video_metadata.get('description', ''),
            uploader_id=uploader_id,
            duration=0,  # Will be set after processing
            file_size=video_metadata['file_size'],
            upload_timestamp=datetime.utcnow(),
            status=VideoStatus.UPLOADING,
            tags=video_metadata.get('tags', []),
            category=video_metadata.get('category', 'general'),
            privacy=video_metadata.get('privacy', 'public')
        )

        # Store in database
        await self.store_video_metadata(video)

        # Initialize multipart upload to S3
        s3_key = f"uploads/{video_id}/{video_metadata['filename']}"
        multipart_upload = self.s3.create_multipart_upload(
            Bucket=self.upload_bucket,
            Key=s3_key,
            ContentType='video/mp4'
        )

        upload_id = multipart_upload['UploadId']

        # Store upload session in Redis
        upload_session = {
            'video_id': video_id,
            'upload_id': upload_id,
            's3_key': s3_key,
            'total_size': video_metadata['file_size'],
            'uploaded_parts': {},
            'created_at': datetime.utcnow().isoformat()
        }

        await self.redis.setex(
            f"upload_session:{video_id}",
            3600,  # 1 hour expiry
            json.dumps(upload_session)
        )

        return {
            'video_id': video_id,
            'upload_id': upload_id,
            'chunk_size': 10 * 1024 * 1024,  # 10MB chunks
            'presigned_urls': await self.generate_presigned_urls(video_id, upload_id, s3_key)
        }

    async def generate_presigned_urls(self, video_id: str, upload_id: str, s3_key: str, max_parts: int = 100) -> List[Dict]:
        """Generate presigned URLs for multipart upload"""
        presigned_urls = []

        for part_number in range(1, max_parts + 1):
            url = self.s3.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': self.upload_bucket,
                    'Key': s3_key,
                    'PartNumber': part_number,
                    'UploadId': upload_id
                },
                ExpiresIn=3600  # 1 hour
            )

            presigned_urls.append({
                'part_number': part_number,
                'url': url
            })

        return presigned_urls

    async def upload_chunk(self, video_id: str, part_number: int, etag: str) -> Dict:
        """Record successful chunk upload"""
        session_key = f"upload_session:{video_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return {'error': 'Upload session not found'}

        session = json.loads(session_data)
        session['uploaded_parts'][str(part_number)] = etag

        # Update session
        await self.redis.setex(session_key, 3600, json.dumps(session))

        return {'success': True, 'uploaded_parts': len(session['uploaded_parts'])}

    async def complete_upload(self, video_id: str) -> Dict:
        """Complete multipart upload and start processing"""
        session_key = f"upload_session:{video_id}"
        session_data = await self.redis.get(session_key)

        if not session_data:
            return {'error': 'Upload session not found'}

        session = json.loads(session_data)

        # Prepare parts for S3 completion
        parts = [
            {'ETag': etag, 'PartNumber': int(part_num)}
            for part_num, etag in session['uploaded_parts'].items()
        ]
        parts.sort(key=lambda x: x['PartNumber'])

        try:
            # Complete multipart upload
            self.s3.complete_multipart_upload(
                Bucket=self.upload_bucket,
                Key=session['s3_key'],
                UploadId=session['upload_id'],
                MultipartUpload={'Parts': parts}
            )

            # Update video status
            await self.update_video_status(video_id, VideoStatus.PROCESSING)

            # Queue for processing
            await self.queue_for_processing(video_id, session['s3_key'])

            # Clean up session
            await self.redis.delete(session_key)

            return {'success': True, 'status': 'processing'}

        except Exception as e:
            logging.error(f"Failed to complete upload for video {video_id}: {e}")
            await self.update_video_status(video_id, VideoStatus.FAILED)
            return {'error': 'Upload completion failed'}

    async def store_video_metadata(self, video: Video):
        """Store video metadata in database"""
        await self.db.execute(
            """
            INSERT INTO videos (video_id, title, description, uploader_id, duration,
                              file_size, upload_timestamp, status, tags, category, privacy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (video.video_id, video.title, video.description, video.uploader_id,
             video.duration, video.file_size, video.upload_timestamp,
             video.status.value, json.dumps(video.tags), video.category, video.privacy)
        )

    async def queue_for_processing(self, video_id: str, s3_key: str):
        """Queue video for processing"""
        processing_job = {
            'video_id': video_id,
            's3_key': s3_key,
            'priority': 'normal',
            'created_at': datetime.utcnow().isoformat()
        }

        await self.processing_queue.put(json.dumps(processing_job))
```

## Video Processing Pipeline

### FFmpeg-based Video Processing

```python
class VideoProcessingService:
    def __init__(self, s3_client, database, redis_client):
        self.s3 = s3_client
        self.db = database
        self.redis = redis_client
        self.source_bucket = "video-uploads"
        self.output_bucket = "video-processed"

    async def process_video(self, video_id: str, s3_key: str):
        """Complete video processing pipeline"""
        try:
            logging.info(f"Starting processing for video {video_id}")

            # Download video from S3
            local_path = f"/tmp/{video_id}_original.mp4"
            await self.download_from_s3(s3_key, local_path)

            # Extract metadata
            metadata = await self.extract_video_metadata(local_path)
            await self.update_video_metadata(video_id, metadata)

            # Generate thumbnail
            thumbnail_path = await self.generate_thumbnail(local_path, video_id)
            thumbnail_url = await self.upload_thumbnail(thumbnail_path, video_id)

            # Transcode to multiple qualities
            processed_formats = await self.transcode_video(local_path, video_id)

            # Create HLS streams
            hls_manifest = await self.create_hls_streams(local_path, video_id)

            # Update database with processing results
            await self.update_processed_video(video_id, {
                'duration': metadata['duration'],
                'thumbnail_url': thumbnail_url,
                'processed_formats': processed_formats,
                'hls_manifest': hls_manifest,
                'status': VideoStatus.READY
            })

            # Clean up temporary files
            await self.cleanup_temp_files(video_id)

            logging.info(f"Successfully processed video {video_id}")

        except Exception as e:
            logging.error(f"Processing failed for video {video_id}: {e}")
            await self.update_video_status(video_id, VideoStatus.FAILED)

    async def extract_video_metadata(self, file_path: str) -> Dict:
        """Extract video metadata using FFprobe"""
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )

            if not video_stream:
                raise ValueError("No video stream found")

            metadata = {
                'duration': float(probe['format']['duration']),
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'fps': eval(video_stream['r_frame_rate']),
                'bitrate': int(probe['format'].get('bit_rate', 0)),
                'codec': video_stream['codec_name']
            }

            return metadata

        except Exception as e:
            logging.error(f"Failed to extract metadata: {e}")
            raise

    async def transcode_video(self, input_path: str, video_id: str) -> Dict[str, str]:
        """Transcode video to multiple qualities"""
        quality_configs = {
            VideoQuality.QUALITY_360P: {'width': 640, 'height': 360, 'bitrate': '800k'},
            VideoQuality.QUALITY_480P: {'width': 854, 'height': 480, 'bitrate': '1200k'},
            VideoQuality.QUALITY_720P: {'width': 1280, 'height': 720, 'bitrate': '2500k'},
            VideoQuality.QUALITY_1080P: {'width': 1920, 'height': 1080, 'bitrate': '4500k'}
        }

        processed_urls = {}

        # Process each quality concurrently
        transcode_tasks = []
        for quality, config in quality_configs.items():
            task = self._transcode_quality(input_path, video_id, quality, config)
            transcode_tasks.append(task)

        results = await asyncio.gather(*transcode_tasks, return_exceptions=True)

        for i, (quality, result) in enumerate(zip(quality_configs.keys(), results)):
            if isinstance(result, Exception):
                logging.error(f"Transcoding failed for {quality.value}: {result}")
            else:
                processed_urls[quality.value] = result

        return processed_urls

    async def _transcode_quality(self, input_path: str, video_id: str, quality: VideoQuality, config: Dict) -> str:
        """Transcode video to specific quality"""
        output_filename = f"{video_id}_{quality.value}.mp4"
        output_path = f"/tmp/{output_filename}"

        try:
            # FFmpeg transcoding
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'scale', config['width'], config['height'])
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                video_bitrate=config['bitrate'],
                acodec='aac',
                audio_bitrate='128k',
                format='mp4'
            )

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ffmpeg.run(stream, overwrite_output=True, quiet=True)
            )

            # Upload to S3
            s3_key = f"processed/{video_id}/{output_filename}"
            await self.upload_to_s3(output_path, s3_key)

            # Generate CDN URL
            cdn_url = f"https://cdn.videostream.com/{s3_key}"

            return cdn_url

        except Exception as e:
            logging.error(f"Transcoding failed for {quality.value}: {e}")
            raise

    async def create_hls_streams(self, input_path: str, video_id: str) -> str:
        """Create HLS (HTTP Live Streaming) segments"""
        hls_dir = f"/tmp/hls_{video_id}"
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: os.makedirs(hls_dir, exist_ok=True)
        )

        # Create adaptive bitrate HLS streams
        qualities = [
            {'name': '360p', 'width': 640, 'height': 360, 'bitrate': '800k'},
            {'name': '720p', 'width': 1280, 'height': 720, 'bitrate': '2500k'},
            {'name': '1080p', 'width': 1920, 'height': 1080, 'bitrate': '4500k'}
        ]

        # Create master playlist
        master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n\n"

        for quality in qualities:
            # Create quality-specific segments
            quality_dir = f"{hls_dir}/{quality['name']}"
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: os.makedirs(quality_dir, exist_ok=True)
            )

            playlist_file = f"{quality_dir}/playlist.m3u8"
            segment_pattern = f"{quality_dir}/segment_%03d.ts"

            # FFmpeg HLS segmentation
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'scale', quality['width'], quality['height'])
            stream = ffmpeg.output(
                stream,
                segment_pattern,
                vcodec='libx264',
                video_bitrate=quality['bitrate'],
                acodec='aac',
                audio_bitrate='128k',
                format='hls',
                hls_time=10,  # 10-second segments
                hls_playlist_type='vod',
                hls_segment_filename=segment_pattern
            )

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ffmpeg.run(stream, overwrite_output=True, quiet=True)
            )

            # Add to master playlist
            bandwidth = int(quality['bitrate'].replace('k', '000'))
            master_playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={quality['width']}x{quality['height']}\n"
            master_playlist += f"{quality['name']}/playlist.m3u8\n\n"

        # Upload HLS files to S3
        await self.upload_hls_to_s3(hls_dir, video_id)

        # Return master playlist URL
        return f"https://cdn.videostream.com/hls/{video_id}/master.m3u8"

    async def generate_thumbnail(self, video_path: str, video_id: str) -> str:
        """Generate video thumbnail"""
        thumbnail_path = f"/tmp/{video_id}_thumbnail.jpg"

        try:
            # Extract frame at 10% of video duration for thumbnail
            stream = ffmpeg.input(video_path, ss='10%')
            stream = ffmpeg.filter(stream, 'scale', 320, 180)
            stream = ffmpeg.output(stream, thumbnail_path, vframes=1, format='image2')

            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ffmpeg.run(stream, overwrite_output=True, quiet=True)
            )

            return thumbnail_path

        except Exception as e:
            logging.error(f"Thumbnail generation failed: {e}")
            raise

    async def upload_thumbnail(self, thumbnail_path: str, video_id: str) -> str:
        """Upload thumbnail to S3 and return URL"""
        s3_key = f"thumbnails/{video_id}.jpg"
        await self.upload_to_s3(thumbnail_path, s3_key)
        return f"https://cdn.videostream.com/{s3_key}"

    async def upload_to_s3(self, local_path: str, s3_key: str):
        """Upload file to S3"""
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.s3.upload_file(local_path, self.output_bucket, s3_key)
        )

    async def upload_hls_to_s3(self, hls_dir: str, video_id: str):
        """Upload HLS files to S3"""
        import os
        for root, dirs, files in os.walk(hls_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, hls_dir)
                s3_key = f"hls/{video_id}/{relative_path}"
                await self.upload_to_s3(local_path, s3_key)
```

## Content Delivery Network

### CDN and Caching Strategy

```python
class CDNService:
    def __init__(self, redis_client, edge_servers):
        self.redis = redis_client
        self.edge_servers = edge_servers
        self.cache_policies = {
            'video_segments': {'ttl': 86400, 'max_size': '1GB'},
            'thumbnails': {'ttl': 604800, 'max_size': '100MB'},
            'manifests': {'ttl': 300, 'max_size': '10MB'}
        }

    async def get_optimal_cdn_url(self, user_location: str, content_type: str, file_path: str) -> str:
        """Get optimal CDN URL based on user location"""
        # Find nearest edge server
        nearest_server = await self.find_nearest_edge_server(user_location)

        # Check if content is cached at edge
        cache_key = f"cdn_cache:{nearest_server['id']}:{file_path}"
        is_cached = await self.redis.exists(cache_key)

        if is_cached:
            return f"https://{nearest_server['domain']}/{file_path}"

        # Content not cached - trigger cache warm-up
        await self.warm_edge_cache(nearest_server, file_path)

        return f"https://{nearest_server['domain']}/{file_path}"

    async def find_nearest_edge_server(self, user_location: str) -> Dict:
        """Find geographically nearest edge server"""
        # Simplified geolocation logic
        location_mapping = {
            'US': {'server_id': 'us-east-1', 'domain': 'us-east-cdn.videostream.com'},
            'EU': {'server_id': 'eu-west-1', 'domain': 'eu-west-cdn.videostream.com'},
            'ASIA': {'server_id': 'ap-southeast-1', 'domain': 'ap-southeast-cdn.videostream.com'}
        }

        region = self.get_region_from_location(user_location)
        return location_mapping.get(region, location_mapping['US'])

    async def warm_edge_cache(self, edge_server: Dict, file_path: str):
        """Pre-load content to edge server"""
        cache_job = {
            'server_id': edge_server['server_id'],
            'file_path': file_path,
            'priority': 'high',
            'timestamp': datetime.utcnow().isoformat()
        }

        await self.redis.lpush('cache_warm_queue', json.dumps(cache_job))

    async def invalidate_cache(self, file_path: str):
        """Invalidate cached content across all edge servers"""
        for server in self.edge_servers:
            cache_key = f"cdn_cache:{server['id']}:{file_path}"
            await self.redis.delete(cache_key)

    async def get_video_streaming_url(self, video_id: str, quality: str, user_location: str) -> str:
        """Get optimized streaming URL for video"""
        # Determine streaming protocol (HLS vs DASH)
        user_agent = "browser"  # Would come from request headers
        protocol = 'hls' if 'Safari' in user_agent else 'dash'

        if protocol == 'hls':
            file_path = f"hls/{video_id}/master.m3u8"
        else:
            file_path = f"dash/{video_id}/manifest.mpd"

        return await self.get_optimal_cdn_url(user_location, 'video_manifest', file_path)

class AdaptiveBitrateStreaming:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_recommended_quality(self, user_id: str, connection_info: Dict) -> str:
        """Recommend video quality based on connection"""
        bandwidth_mbps = connection_info.get('bandwidth_mbps', 5)
        device_type = connection_info.get('device_type', 'desktop')

        # Quality recommendations based on bandwidth
        if bandwidth_mbps >= 8:
            recommended_quality = '1080p'
        elif bandwidth_mbps >= 4:
            recommended_quality = '720p'
        elif bandwidth_mbps >= 2:
            recommended_quality = '480p'
        else:
            recommended_quality = '360p'

        # Adjust for mobile devices
        if device_type == 'mobile' and recommended_quality in ['1080p', '720p']:
            recommended_quality = '480p'

        # Store user preference
        await self.redis.setex(f"user_quality:{user_id}", 3600, recommended_quality)

        return recommended_quality

    async def update_streaming_quality(self, user_id: str, current_buffer_health: float, network_conditions: Dict):
        """Dynamically adjust streaming quality"""
        current_quality = await self.redis.get(f"user_quality:{user_id}") or '480p'

        # Buffer health analysis
        if current_buffer_health < 0.3:  # Less than 30% buffer
            # Reduce quality to prevent buffering
            new_quality = self.downgrade_quality(current_quality)
        elif current_buffer_health > 0.8 and network_conditions['bandwidth_mbps'] > 6:
            # Upgrade quality if buffer is healthy and bandwidth allows
            new_quality = self.upgrade_quality(current_quality)
        else:
            new_quality = current_quality

        if new_quality != current_quality:
            await self.redis.setex(f"user_quality:{user_id}", 3600, new_quality)

        return new_quality

    def downgrade_quality(self, current_quality: str) -> str:
        """Downgrade video quality"""
        quality_ladder = ['360p', '480p', '720p', '1080p']
        current_index = quality_ladder.index(current_quality)
        return quality_ladder[max(0, current_index - 1)]

    def upgrade_quality(self, current_quality: str) -> str:
        """Upgrade video quality"""
        quality_ladder = ['360p', '480p', '720p', '1080p']
        current_index = quality_ladder.index(current_quality)
        return quality_ladder[min(len(quality_ladder) - 1, current_index + 1)]
```

## Recommendation Engine

### ML-based Video Recommendations

```python
class RecommendationEngine:
    def __init__(self, database, redis_client):
        self.db = database
        self.redis = redis_client
        self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')

    async def get_recommendations(self, user_id: str, count: int = 20) -> List[str]:
        """Get personalized video recommendations"""
        # Try cache first
        cache_key = f"recommendations:{user_id}"
        cached_recs = await self.redis.get(cache_key)

        if cached_recs:
            return json.loads(cached_recs)[:count]

        # Generate fresh recommendations
        recommendations = await self.generate_recommendations(user_id, count * 2)

        # Cache for 1 hour
        await self.redis.setex(cache_key, 3600, json.dumps(recommendations))

        return recommendations[:count]

    async def generate_recommendations(self, user_id: str, count: int) -> List[str]:
        """Generate recommendations using multiple strategies"""
        # Get user viewing history
        user_history = await self.get_user_viewing_history(user_id)

        if not user_history:
            # New user - return trending videos
            return await self.get_trending_videos(count)

        # Combine multiple recommendation strategies
        collaborative_recs = await self.collaborative_filtering(user_id, count // 3)
        content_based_recs = await self.content_based_filtering(user_id, count // 3)
        trending_recs = await self.get_trending_videos(count // 3)

        # Merge and deduplicate
        all_recommendations = collaborative_recs + content_based_recs + trending_recs
        unique_recs = list(dict.fromkeys(all_recommendations))  # Remove duplicates

        return unique_recs[:count]

    async def collaborative_filtering(self, user_id: str, count: int) -> List[str]:
        """Collaborative filtering based on similar users"""
        # Find users with similar viewing patterns
        similar_users = await self.find_similar_users(user_id, limit=50)

        # Get videos watched by similar users but not by current user
        user_watched = await self.get_user_watched_videos(user_id)

        recommendations = []
        for similar_user in similar_users:
            similar_user_videos = await self.get_user_watched_videos(similar_user['user_id'])
            new_videos = set(similar_user_videos) - set(user_watched)

            for video_id in new_videos:
                if len(recommendations) < count:
                    recommendations.append(video_id)

        return recommendations

    async def content_based_filtering(self, user_id: str, count: int) -> List[str]:
        """Content-based filtering using video features"""
        # Get user's preferred categories and tags
        user_preferences = await self.analyze_user_preferences(user_id)

        # Find videos matching user preferences
        similar_videos = await self.find_similar_content(user_preferences, count)

        return similar_videos

    async def find_similar_users(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Find users with similar viewing patterns"""
        # Get user's viewing vector
        user_vector = await self.get_user_feature_vector(user_id)

        # Compare with other users using cosine similarity
        query = """
        SELECT u2.user_id,
               SUM(CASE WHEN u1.video_id = u2.video_id THEN 1 ELSE 0 END) as common_videos
        FROM user_views u1
        JOIN user_views u2 ON u1.video_id = u2.video_id
        WHERE u1.user_id = ? AND u2.user_id != ?
        GROUP BY u2.user_id
        HAVING common_videos >= 3
        ORDER BY common_videos DESC
        LIMIT ?
        """

        similar_users = await self.db.fetch_all(query, (user_id, user_id, limit))
        return similar_users

    async def analyze_user_preferences(self, user_id: str) -> Dict:
        """Analyze user's content preferences"""
        query = """
        SELECT v.category, COUNT(*) as category_count,
               v.tags, AVG(uv.watch_time / v.duration) as completion_rate
        FROM user_views uv
        JOIN videos v ON uv.video_id = v.video_id
        WHERE uv.user_id = ?
        GROUP BY v.category
        ORDER BY category_count DESC
        """

        preferences = await self.db.fetch_all(query, (user_id,))

        # Extract preferred categories and tags
        preferred_categories = [p['category'] for p in preferences[:5]]

        # Aggregate tags from watched videos
        all_tags = []
        for pref in preferences:
            if pref['tags']:
                all_tags.extend(json.loads(pref['tags']))

        # Get most common tags
        from collections import Counter
        tag_counts = Counter(all_tags)
        preferred_tags = [tag for tag, count in tag_counts.most_common(10)]

        return {
            'categories': preferred_categories,
            'tags': preferred_tags,
            'completion_rates': {p['category']: p['completion_rate'] for p in preferences}
        }

    async def find_similar_content(self, user_preferences: Dict, count: int) -> List[str]:
        """Find videos similar to user preferences"""
        # Build query based on preferences
        category_filter = "(" + ",".join([f"'{cat}'" for cat in user_preferences['categories']]) + ")"

        query = f"""
        SELECT video_id, title, description, tags, category,
               view_count, like_count
        FROM videos
        WHERE category IN {category_filter}
        AND status = 'ready'
        AND privacy = 'public'
        ORDER BY (like_count / NULLIF(view_count, 0)) DESC
        LIMIT ?
        """

        similar_videos = await self.db.fetch_all(query, (count * 2,))

        # Score videos based on tag similarity
        scored_videos = []
        for video in similar_videos:
            video_tags = json.loads(video['tags']) if video['tags'] else []
            tag_similarity = len(set(video_tags) & set(user_preferences['tags'])) / max(len(user_preferences['tags']), 1)

            score = (
                tag_similarity * 0.6 +
                (video['like_count'] / max(video['view_count'], 1)) * 0.4
            )

            scored_videos.append((video['video_id'], score))

        # Sort by score and return top videos
        scored_videos.sort(key=lambda x: x[1], reverse=True)
        return [video_id for video_id, score in scored_videos[:count]]

    async def update_user_interaction(self, user_id: str, video_id: str, interaction_type: str, value: float = 1.0):
        """Update user interaction data for better recommendations"""
        interaction = {
            'user_id': user_id,
            'video_id': video_id,
            'interaction_type': interaction_type,  # 'view', 'like', 'share', 'comment'
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store interaction
        await self.db.execute(
            "INSERT INTO user_interactions (user_id, video_id, interaction_type, value, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, video_id, interaction_type, value, datetime.utcnow())
        )

        # Invalidate cached recommendations
        await self.redis.delete(f"recommendations:{user_id}")

    async def get_trending_videos(self, count: int) -> List[str]:
        """Get currently trending videos"""
        # Calculate trending score based on recent views and engagement
        query = """
        SELECT v.video_id,
               COUNT(uv.view_id) as recent_views,
               v.like_count,
               v.view_count,
               (COUNT(uv.view_id) * 0.6 + v.like_count * 0.4) as trending_score
        FROM videos v
        LEFT JOIN user_views uv ON v.video_id = uv.video_id
            AND uv.timestamp > DATE_SUB(NOW(), INTERVAL 24 HOUR)
        WHERE v.status = 'ready' AND v.privacy = 'public'
        GROUP BY v.video_id
        ORDER BY trending_score DESC
        LIMIT ?
        """

        trending = await self.db.fetch_all(query, (count,))
        return [video['video_id'] for video in trending]
```

## Live Streaming

### Real-time Live Streaming Service

```python
class LiveStreamingService:
    def __init__(self, redis_client, database, rtmp_server):
        self.redis = redis_client
        self.db = database
        self.rtmp_server = rtmp_server
        self.active_streams = {}

    async def start_live_stream(self, streamer_id: str, stream_metadata: Dict) -> Dict:
        """Start a new live stream"""
        stream_id = str(uuid.uuid4())
        stream_key = self.generate_stream_key()

        live_stream = LiveStream(
            stream_id=stream_id,
            streamer_id=streamer_id,
            title=stream_metadata['title'],
            description=stream_metadata.get('description', ''),
            category=stream_metadata.get('category', 'general'),
            start_time=datetime.utcnow(),
            stream_key=stream_key
        )

        # Store stream metadata
        await self.store_live_stream(live_stream)

        # Configure RTMP endpoint
        rtmp_url = f"rtmp://ingest.videostream.com/live/{stream_key}"

        # Set up HLS output for viewers
        hls_url = f"https://live-cdn.videostream.com/hls/{stream_id}/master.m3u8"

        # Start stream processing
        await self.setup_live_transcoding(stream_id, stream_key)

        self.active_streams[stream_id] = live_stream

        return {
            'stream_id': stream_id,
            'rtmp_url': rtmp_url,
            'hls_url': hls_url,
            'stream_key': stream_key
        }

    async def setup_live_transcoding(self, stream_id: str, stream_key: str):
        """Set up real-time transcoding for live stream"""
        # Configure FFmpeg for live transcoding to multiple qualities
        transcoding_config = {
            'input': f"rtmp://localhost:1935/live/{stream_key}",
            'outputs': [
                {
                    'quality': '360p',
                    'video_bitrate': '800k',
                    'audio_bitrate': '128k',
                    'hls_path': f"/tmp/hls/{stream_id}/360p/"
                },
                {
                    'quality': '720p',
                    'video_bitrate': '2500k',
                    'audio_bitrate': '128k',
                    'hls_path': f"/tmp/hls/{stream_id}/720p/"
                },
                {
                    'quality': '1080p',
                    'video_bitrate': '4500k',
                    'audio_bitrate': '128k',
                    'hls_path': f"/tmp/hls/{stream_id}/1080p/"
                }
            ]
        }

        # Start transcoding process
        await self.start_live_transcoding_process(transcoding_config)

    async def handle_viewer_join(self, stream_id: str, viewer_id: str):
        """Handle viewer joining live stream"""
        if stream_id in self.active_streams:
            # Increment viewer count
            await self.redis.incr(f"stream_viewers:{stream_id}")

            # Update max viewers if necessary
            current_viewers = await self.redis.get(f"stream_viewers:{stream_id}")
            stream = self.active_streams[stream_id]

            if int(current_viewers) > stream.max_viewers:
                stream.max_viewers = int(current_viewers)
                await self.update_stream_metrics(stream_id, {'max_viewers': stream.max_viewers})

            # Add viewer to stream
            await self.redis.sadd(f"stream_viewers_set:{stream_id}", viewer_id)

            # Send stream metadata to viewer
            return {
                'stream_title': stream.title,
                'streamer_id': stream.streamer_id,
                'current_viewers': int(current_viewers),
                'start_time': stream.start_time.isoformat()
            }

    async def handle_viewer_leave(self, stream_id: str, viewer_id: str):
        """Handle viewer leaving live stream"""
        if stream_id in self.active_streams:
            # Decrement viewer count
            await self.redis.decr(f"stream_viewers:{stream_id}")

            # Remove viewer from stream
            await self.redis.srem(f"stream_viewers_set:{stream_id}", viewer_id)

    async def end_live_stream(self, stream_id: str, streamer_id: str):
        """End live stream"""
        if stream_id not in self.active_streams:
            return {'error': 'Stream not found'}

        stream = self.active_streams[stream_id]

        if stream.streamer_id != streamer_id:
            return {'error': 'Unauthorized'}

        # Update stream end time
        stream.end_time = datetime.utcnow()
        stream.status = 'ended'

        # Calculate final metrics
        final_metrics = {
            'end_time': stream.end_time,
            'duration': (stream.end_time - stream.start_time).total_seconds(),
            'max_viewers': stream.max_viewers,
            'status': 'ended'
        }

        # Update database
        await self.update_stream_metrics(stream_id, final_metrics)

        # Stop transcoding
        await self.stop_live_transcoding(stream_id)

        # Clean up Redis data
        await self.redis.delete(f"stream_viewers:{stream_id}")
        await self.redis.delete(f"stream_viewers_set:{stream_id}")

        # Remove from active streams
        del self.active_streams[stream_id]

        return {'success': True, 'final_metrics': final_metrics}

    async def get_live_chat_messages(self, stream_id: str, limit: int = 50) -> List[Dict]:
        """Get recent chat messages for live stream"""
        messages = await self.redis.lrange(f"chat:{stream_id}", -limit, -1)
        return [json.loads(msg) for msg in messages]

    async def send_chat_message(self, stream_id: str, user_id: str, message: str):
        """Send chat message to live stream"""
        chat_message = {
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store in Redis list (keep last 1000 messages)
        await self.redis.lpush(f"chat:{stream_id}", json.dumps(chat_message))
        await self.redis.ltrim(f"chat:{stream_id}", 0, 999)

        # Broadcast to all viewers via WebSocket
        await self.broadcast_chat_message(stream_id, chat_message)

    def generate_stream_key(self) -> str:
        """Generate unique stream key"""
        return hashlib.sha256(f"{uuid.uuid4()}{datetime.utcnow()}".encode()).hexdigest()[:16]
```

This comprehensive video streaming platform implementation covers all major components needed for a production-ready service: video upload and processing, CDN distribution, personalized recommendations, and live streaming capabilities. The system is designed to handle millions of users and petabytes of content with high availability and optimal performance.