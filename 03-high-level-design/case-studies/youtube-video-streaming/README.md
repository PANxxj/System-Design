# YouTube Video Streaming System Design 🔴

## 🎯 Learning Objectives
- Design a global video streaming platform at massive scale
- Handle billions of video uploads and views daily
- Implement efficient video processing and CDN distribution
- Design recommendation and search systems for content discovery

## 📋 Problem Statement

Design a video streaming platform like YouTube that can:

1. **Video Upload & Processing**: Support millions of video uploads daily
2. **Global Streaming**: Serve billions of video views worldwide
3. **Content Discovery**: Search, recommendations, trending videos
4. **Social Features**: Comments, likes, subscriptions, notifications
5. **Content Management**: Creator tools, analytics, monetization
6. **Live Streaming**: Real-time video broadcasting
7. **Mobile & Web**: Multi-platform support with adaptive streaming

## 📊 Scale Estimation

### Traffic Estimates
- **Registered Users**: 2+ billion
- **Daily Active Users**: 800 million
- **Videos Uploaded Daily**: 500 hours/minute = 720,000 hours/day
- **Video Views Daily**: 5 billion views
- **Peak Concurrent Viewers**: 100 million
- **Storage Growth**: 1 petabyte/day

### Storage Estimates
```python
# Video Upload Estimates
hours_uploaded_per_day = 720_000  # 500 hours/minute
average_video_length_minutes = 15
videos_uploaded_per_day = (hours_uploaded_per_day * 60) / average_video_length_minutes
# = 2.88 million videos/day

# Storage per video (multiple formats)
storage_per_video = {
    '360p': 50,    # MB per hour
    '720p': 150,   # MB per hour
    '1080p': 400,  # MB per hour
    '1440p': 800,  # MB per hour
    '4K': 2000,    # MB per hour
}

total_storage_per_hour = sum(storage_per_video.values())  # 3.4 GB/hour
daily_storage_raw = hours_uploaded_per_day * total_storage_per_hour
# = 2.45 TB/day for video files

# With thumbnails, metadata, indexes
daily_storage_total = daily_storage_raw * 1.2  # 2.94 TB/day
annual_storage = daily_storage_total * 365  # 1.07 PB/year
```

### Bandwidth Estimates
```python
# Viewing Estimates
daily_views = 5_000_000_000
average_view_duration_minutes = 10
concurrent_peak_viewers = 100_000_000

# Bandwidth calculation (assuming 1080p average)
average_bitrate_mbps = 5  # Mbps for 1080p
peak_bandwidth_gbps = (concurrent_peak_viewers * average_bitrate_mbps) / 1000
# = 500,000 Gbps = 500 Tbps peak bandwidth
```

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile Apps   │    │   Web Clients   │    │   Smart TVs     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌─────────────────▼─────────────────┐
                │          Global CDN              │
                │    (Multiple Providers)          │
                └─────────────────┬─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│  Video Upload  │    │  Video Streaming │    │   API Gateway    │
│   Service      │    │    Service       │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Video Processing│    │  Recommendation  │    │  Search Service  │
│   Pipeline     │    │    Engine        │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Content Store  │    │  Analytics DB    │    │   Metadata DB    │
│ (Object Store) │    │   (BigQuery)     │    │   (Cassandra)    │
└────────────────┘    └──────────────────┘    └──────────────────┘
```

### Core Components Design

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import uuid

# Enums
class VideoStatus(Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROCESSED = "processed"
    PUBLISHED = "published"
    PRIVATE = "private"
    DELETED = "deleted"

class VideoQuality(Enum):
    QUALITY_360P = "360p"
    QUALITY_720P = "720p"
    QUALITY_1080P = "1080p"
    QUALITY_1440P = "1440p"
    QUALITY_4K = "4k"

class ContentType(Enum):
    VIDEO = "video"
    LIVE_STREAM = "live_stream"
    SHORT = "short"
    PREMIERE = "premiere"

# Core Models
@dataclass
class User:
    user_id: str
    username: str
    email: str
    display_name: str
    avatar_url: Optional[str]
    subscriber_count: int = 0
    video_count: int = 0
    total_views: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    verified: bool = False

@dataclass
class Channel:
    channel_id: str
    user_id: str
    name: str
    description: str
    banner_url: Optional[str]
    subscriber_count: int = 0
    total_views: int = 0
    video_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Video:
    video_id: str
    channel_id: str
    title: str
    description: str
    thumbnail_url: str
    duration_seconds: int
    status: VideoStatus
    content_type: ContentType
    view_count: int = 0
    like_count: int = 0
    dislike_count: int = 0
    comment_count: int = 0
    upload_date: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    category: str = "Entertainment"
    language: str = "en"
    age_restriction: bool = False

@dataclass
class VideoFile:
    file_id: str
    video_id: str
    quality: VideoQuality
    format: str  # mp4, webm, etc.
    file_size_bytes: int
    bitrate_kbps: int
    width: int
    height: int
    cdn_url: str
    checksum: str

@dataclass
class Comment:
    comment_id: str
    video_id: str
    user_id: str
    content: str
    like_count: int = 0
    reply_count: int = 0
    parent_comment_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_pinned: bool = False
```

## 🎥 Video Upload and Processing Service

```python
import asyncio
import aiofiles
from typing import BinaryIO
import tempfile
import subprocess
import json

class VideoUploadService:
    def __init__(self, storage_service, processing_queue, metadata_service):
        self.storage = storage_service
        self.processing_queue = processing_queue
        self.metadata = metadata_service
        self.chunk_size = 8 * 1024 * 1024  # 8MB chunks

    async def upload_video(self, user_id: str, file_stream: BinaryIO,
                          metadata: Dict) -> str:
        """Handle video upload with resumable uploads"""
        video_id = str(uuid.uuid4())

        # Create video record
        video = Video(
            video_id=video_id,
            channel_id=metadata["channel_id"],
            title=metadata["title"],
            description=metadata["description"],
            thumbnail_url="",
            duration_seconds=0,
            status=VideoStatus.UPLOADING,
            content_type=ContentType(metadata["content_type"])
        )

        await self.metadata.save_video(video)

        # Upload raw video file
        raw_file_key = f"raw_videos/{video_id}/original.{metadata['format']}"

        try:
            # Resumable upload in chunks
            await self._upload_in_chunks(file_stream, raw_file_key)

            # Update status and queue for processing
            video.status = VideoStatus.PROCESSING
            await self.metadata.update_video_status(video_id, VideoStatus.PROCESSING)

            # Queue for processing
            await self.processing_queue.enqueue({
                "video_id": video_id,
                "raw_file_key": raw_file_key,
                "metadata": metadata
            })

            return video_id

        except Exception as e:
            # Handle upload failure
            video.status = VideoStatus.DELETED
            await self.metadata.update_video_status(video_id, VideoStatus.DELETED)
            await self.storage.delete(raw_file_key)
            raise e

    async def _upload_in_chunks(self, file_stream: BinaryIO, file_key: str):
        """Upload file in chunks for resumability"""
        chunk_index = 0
        upload_id = await self.storage.initiate_multipart_upload(file_key)

        try:
            parts = []
            while True:
                chunk = file_stream.read(self.chunk_size)
                if not chunk:
                    break

                # Upload chunk
                part_response = await self.storage.upload_part(
                    file_key, upload_id, chunk_index + 1, chunk
                )
                parts.append({
                    "PartNumber": chunk_index + 1,
                    "ETag": part_response["ETag"]
                })
                chunk_index += 1

            # Complete multipart upload
            await self.storage.complete_multipart_upload(file_key, upload_id, parts)

        except Exception as e:
            # Abort upload on failure
            await self.storage.abort_multipart_upload(file_key, upload_id)
            raise e

class VideoProcessingService:
    def __init__(self, storage_service, cdn_service, metadata_service):
        self.storage = storage_service
        self.cdn = cdn_service
        self.metadata = metadata_service

    async def process_video(self, job: Dict):
        """Process uploaded video"""
        video_id = job["video_id"]
        raw_file_key = job["raw_file_key"]

        try:
            # Download raw video
            with tempfile.NamedTemporaryFile() as temp_file:
                await self.storage.download_to_file(raw_file_key, temp_file.name)

                # Extract metadata
                video_metadata = await self._extract_video_metadata(temp_file.name)

                # Generate thumbnails
                thumbnails = await self._generate_thumbnails(temp_file.name, video_id)

                # Transcode to multiple qualities
                transcoded_files = await self._transcode_video(temp_file.name, video_id)

                # Upload processed files to CDN
                await self._upload_to_cdn(transcoded_files, thumbnails, video_id)

                # Update video metadata
                await self._update_video_metadata(video_id, video_metadata,
                                                transcoded_files, thumbnails)

                # Mark as processed
                await self.metadata.update_video_status(video_id, VideoStatus.PROCESSED)

        except Exception as e:
            # Mark as failed
            await self.metadata.update_video_status(video_id, VideoStatus.DELETED)
            raise e
        finally:
            # Clean up raw file
            await self.storage.delete(raw_file_key)

    async def _extract_video_metadata(self, file_path: str) -> Dict:
        """Extract video metadata using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to extract metadata: {result.stderr}")

        probe_data = json.loads(result.stdout)
        video_stream = next(s for s in probe_data['streams'] if s['codec_type'] == 'video')

        return {
            'duration': float(probe_data['format']['duration']),
            'width': int(video_stream['width']),
            'height': int(video_stream['height']),
            'frame_rate': eval(video_stream['r_frame_rate']),
            'bitrate': int(probe_data['format'].get('bit_rate', 0))
        }

    async def _generate_thumbnails(self, file_path: str, video_id: str) -> List[str]:
        """Generate video thumbnails"""
        thumbnails = []
        output_dir = f"/tmp/thumbnails/{video_id}"

        # Create directory
        subprocess.run(['mkdir', '-p', output_dir])

        # Generate thumbnails at different timestamps
        timestamps = ['00:00:01', '25%', '50%', '75%']

        for i, timestamp in enumerate(timestamps):
            thumbnail_path = f"{output_dir}/thumb_{i}.jpg"

            cmd = [
                'ffmpeg', '-i', file_path, '-ss', timestamp,
                '-vframes', '1', '-q:v', '2', '-y', thumbnail_path
            ]

            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                thumbnails.append(thumbnail_path)

        return thumbnails

    async def _transcode_video(self, file_path: str, video_id: str) -> Dict[str, str]:
        """Transcode video to multiple qualities"""
        output_dir = f"/tmp/transcoded/{video_id}"
        subprocess.run(['mkdir', '-p', output_dir])

        # Transcoding configurations
        configs = {
            VideoQuality.QUALITY_360P: {
                'resolution': '640x360',
                'bitrate': '400k',
                'bufsize': '800k'
            },
            VideoQuality.QUALITY_720P: {
                'resolution': '1280x720',
                'bitrate': '1500k',
                'bufsize': '3000k'
            },
            VideoQuality.QUALITY_1080P: {
                'resolution': '1920x1080',
                'bitrate': '4000k',
                'bufsize': '8000k'
            },
            VideoQuality.QUALITY_1440P: {
                'resolution': '2560x1440',
                'bitrate': '8000k',
                'bufsize': '16000k'
            },
            VideoQuality.QUALITY_4K: {
                'resolution': '3840x2160',
                'bitrate': '20000k',
                'bufsize': '40000k'
            }
        }

        transcoded_files = {}

        # Parallel transcoding
        tasks = []
        for quality, config in configs.items():
            task = self._transcode_single_quality(
                file_path, output_dir, quality, config
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for quality, result in zip(configs.keys(), results):
            if not isinstance(result, Exception):
                transcoded_files[quality.value] = result

        return transcoded_files

    async def _transcode_single_quality(self, input_path: str, output_dir: str,
                                      quality: VideoQuality, config: Dict) -> str:
        """Transcode to single quality"""
        output_path = f"{output_dir}/{quality.value}.mp4"

        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264', '-preset', 'medium',
            '-b:v', config['bitrate'], '-bufsize', config['bufsize'],
            '-vf', f"scale={config['resolution']}",
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',  # Optimize for streaming
            '-y', output_path
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Transcoding failed for {quality.value}: {stderr.decode()}")

        return output_path

    async def _upload_to_cdn(self, transcoded_files: Dict, thumbnails: List[str],
                           video_id: str):
        """Upload processed files to CDN"""
        # Upload video files
        for quality, file_path in transcoded_files.items():
            cdn_key = f"videos/{video_id}/{quality}.mp4"
            await self.cdn.upload_file(file_path, cdn_key)

        # Upload thumbnails
        for i, thumbnail_path in enumerate(thumbnails):
            cdn_key = f"thumbnails/{video_id}/thumb_{i}.jpg"
            await self.cdn.upload_file(thumbnail_path, cdn_key)

    async def _update_video_metadata(self, video_id: str, metadata: Dict,
                                   transcoded_files: Dict, thumbnails: List[str]):
        """Update video metadata in database"""
        # Create video file records
        video_files = []
        for quality, file_path in transcoded_files.items():
            file_size = await self._get_file_size(file_path)

            video_file = VideoFile(
                file_id=str(uuid.uuid4()),
                video_id=video_id,
                quality=VideoQuality(quality),
                format="mp4",
                file_size_bytes=file_size,
                bitrate_kbps=self._get_bitrate_for_quality(quality),
                width=self._get_width_for_quality(quality),
                height=self._get_height_for_quality(quality),
                cdn_url=f"https://cdn.youtube.com/videos/{video_id}/{quality}.mp4",
                checksum=""
            )
            video_files.append(video_file)

        # Update video record
        await self.metadata.update_video_metadata(
            video_id=video_id,
            duration_seconds=int(metadata['duration']),
            thumbnail_url=f"https://cdn.youtube.com/thumbnails/{video_id}/thumb_0.jpg",
            video_files=video_files
        )
```

## 📺 Video Streaming Service

```python
class VideoStreamingService:
    def __init__(self, cdn_service, analytics_service, cache_service):
        self.cdn = cdn_service
        self.analytics = analytics_service
        self.cache = cache_service

    async def get_video_stream_url(self, video_id: str, quality: str,
                                 user_location: Dict, device_type: str) -> Dict:
        """Get optimized streaming URL for user"""
        # Get video metadata
        video_metadata = await self.cache.get_video_metadata(video_id)
        if not video_metadata:
            video_metadata = await self.metadata.get_video(video_id)
            await self.cache.cache_video_metadata(video_id, video_metadata)

        # Determine best CDN edge server
        edge_server = await self.cdn.get_nearest_edge_server(
            user_location, video_id
        )

        # Check if video is cached at edge
        is_cached = await self.cdn.is_video_cached(edge_server, video_id, quality)

        if not is_cached:
            # Pre-warm cache for popular videos
            await self.cdn.prefetch_video(edge_server, video_id, quality)

        # Generate signed streaming URL
        stream_url = await self.cdn.generate_signed_url(
            video_id, quality, edge_server, expires_in=3600
        )

        # Adaptive bitrate streaming manifest
        manifest_url = await self._generate_adaptive_manifest(
            video_id, video_metadata, edge_server
        )

        return {
            "stream_url": stream_url,
            "manifest_url": manifest_url,
            "available_qualities": video_metadata["available_qualities"],
            "duration": video_metadata["duration"],
            "thumbnail_url": video_metadata["thumbnail_url"]
        }

    async def _generate_adaptive_manifest(self, video_id: str,
                                        video_metadata: Dict, edge_server: str) -> str:
        """Generate HLS/DASH manifest for adaptive streaming"""
        manifest = {
            "version": 6,
            "playlists": []
        }

        # Add quality levels
        for quality in video_metadata["available_qualities"]:
            quality_data = video_metadata["qualities"][quality]

            playlist = {
                "uri": f"https://{edge_server}/videos/{video_id}/{quality}.m3u8",
                "bandwidth": quality_data["bitrate"] * 1000,
                "resolution": {
                    "width": quality_data["width"],
                    "height": quality_data["height"]
                },
                "codecs": "avc1.42E01E,mp4a.40.2"
            }
            manifest["playlists"].append(playlist)

        # Upload manifest to CDN
        manifest_key = f"manifests/{video_id}/master.m3u8"
        await self.cdn.upload_manifest(manifest_key, manifest)

        return f"https://{edge_server}/{manifest_key}"

    async def record_view(self, video_id: str, user_id: Optional[str],
                         session_data: Dict):
        """Record video view for analytics"""
        view_event = {
            "video_id": video_id,
            "user_id": user_id,
            "session_id": session_data["session_id"],
            "timestamp": datetime.now(),
            "watch_time_seconds": session_data["watch_time"],
            "quality_changes": session_data["quality_changes"],
            "device_type": session_data["device_type"],
            "location": session_data["location"],
            "referrer": session_data.get("referrer"),
            "buffering_events": session_data["buffering_events"]
        }

        # Real-time analytics
        await self.analytics.record_view_event(view_event)

        # Update view count (eventual consistency)
        await self.analytics.increment_view_count(video_id)

        # Update watch time analytics
        await self.analytics.update_watch_time(video_id, session_data["watch_time"])

class CDNService:
    def __init__(self):
        self.edge_servers = {
            "us-east": ["cdn1.us-east.youtube.com", "cdn2.us-east.youtube.com"],
            "us-west": ["cdn1.us-west.youtube.com", "cdn2.us-west.youtube.com"],
            "eu-west": ["cdn1.eu-west.youtube.com", "cdn2.eu-west.youtube.com"],
            "asia-pacific": ["cdn1.asia.youtube.com", "cdn2.asia.youtube.com"]
        }

    async def get_nearest_edge_server(self, user_location: Dict, video_id: str) -> str:
        """Get nearest edge server with video cached"""
        user_region = self._determine_region(user_location)

        # Check server load and video availability
        available_servers = self.edge_servers[user_region]

        best_server = None
        min_load = float('inf')

        for server in available_servers:
            load = await self._get_server_load(server)
            has_video = await self.is_video_cached(server, video_id, "1080p")

            # Prefer servers that already have the video
            if has_video:
                load *= 0.5

            if load < min_load:
                min_load = load
                best_server = server

        return best_server

    async def prefetch_video(self, edge_server: str, video_id: str, quality: str):
        """Prefetch video to edge server"""
        origin_url = f"https://origin.youtube.com/videos/{video_id}/{quality}.mp4"

        # Trigger prefetch
        await self._send_prefetch_request(edge_server, video_id, quality, origin_url)

    def _determine_region(self, location: Dict) -> str:
        """Determine CDN region based on user location"""
        country = location.get("country", "US")

        if country in ["US", "CA", "MX"]:
            # Further refinement based on latitude/longitude
            if location.get("longitude", 0) > -100:
                return "us-east"
            else:
                return "us-west"
        elif country in ["GB", "FR", "DE", "ES", "IT"]:
            return "eu-west"
        else:
            return "asia-pacific"
```

## 🔍 Search and Recommendation Service

```python
import elasticsearch
from typing import List, Dict

class VideoSearchService:
    def __init__(self, elasticsearch_client, analytics_service):
        self.es = elasticsearch_client
        self.analytics = analytics_service

    async def search_videos(self, query: str, filters: Dict = None,
                          user_id: str = None, page: int = 1,
                          page_size: int = 20) -> Dict:
        """Search videos with personalization"""

        # Build Elasticsearch query
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "title^3",
                                    "description^2",
                                    "tags^2",
                                    "channel_name^1.5",
                                    "transcript"
                                ],
                                "type": "best_fields",
                                "fuzziness": "AUTO"
                            }
                        }
                    ],
                    "filter": [],
                    "should": []  # Personalization boosts
                }
            },
            "sort": [],
            "from": (page - 1) * page_size,
            "size": page_size,
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {}
                }
            }
        }

        # Apply filters
        if filters:
            if "duration" in filters:
                duration_filter = self._build_duration_filter(filters["duration"])
                search_query["query"]["bool"]["filter"].append(duration_filter)

            if "upload_date" in filters:
                date_filter = self._build_date_filter(filters["upload_date"])
                search_query["query"]["bool"]["filter"].append(date_filter)

            if "category" in filters:
                search_query["query"]["bool"]["filter"].append({
                    "term": {"category": filters["category"]}
                })

        # Personalization
        if user_id:
            personalization_boosts = await self._get_personalization_boosts(user_id)
            search_query["query"]["bool"]["should"].extend(personalization_boosts)

        # Popularity boost
        search_query["query"]["bool"]["should"].append({
            "function_score": {
                "field_value_factor": {
                    "field": "view_count",
                    "modifier": "log1p",
                    "factor": 0.1
                }
            }
        })

        # Recency boost
        search_query["query"]["bool"]["should"].append({
            "function_score": {
                "gauss": {
                    "upload_date": {
                        "origin": "now",
                        "scale": "7d",
                        "decay": 0.5
                    }
                }
            }
        })

        # Execute search
        response = await self.es.search(
            index="videos",
            body=search_query
        )

        # Process results
        videos = []
        for hit in response["hits"]["hits"]:
            video = hit["_source"]
            video["score"] = hit["_score"]

            if "highlight" in hit:
                video["highlights"] = hit["highlight"]

            videos.append(video)

        # Log search for analytics
        await self.analytics.log_search(query, user_id, len(videos))

        return {
            "videos": videos,
            "total": response["hits"]["total"]["value"],
            "page": page,
            "page_size": page_size,
            "took_ms": response["took"]
        }

    async def _get_personalization_boosts(self, user_id: str) -> List[Dict]:
        """Get personalization boosts based on user history"""
        user_preferences = await self.analytics.get_user_preferences(user_id)

        boosts = []

        # Boost preferred categories
        for category, weight in user_preferences.get("categories", {}).items():
            boosts.append({
                "term": {
                    "category": {
                        "value": category,
                        "boost": weight
                    }
                }
            })

        # Boost subscribed channels
        subscribed_channels = user_preferences.get("subscribed_channels", [])
        if subscribed_channels:
            boosts.append({
                "terms": {
                    "channel_id": subscribed_channels,
                    "boost": 2.0
                }
            })

        return boosts

class RecommendationEngine:
    def __init__(self, ml_service, analytics_service, graph_service):
        self.ml_service = ml_service
        self.analytics = analytics_service
        self.graph_service = graph_service

    async def get_recommendations(self, user_id: str, context: Dict = None) -> List[str]:
        """Get personalized video recommendations"""

        # Get user watching history and preferences
        user_profile = await self.analytics.get_user_profile(user_id)

        # Multiple recommendation strategies
        strategies = [
            self._collaborative_filtering,
            self._content_based_filtering,
            self._trending_boost,
            self._subscription_feed,
            self._similar_videos
        ]

        # Get recommendations from each strategy
        all_recommendations = []
        for strategy in strategies:
            recs = await strategy(user_id, user_profile, context)
            all_recommendations.extend(recs)

        # Combine and rank recommendations
        final_recommendations = await self._hybrid_ranking(
            all_recommendations, user_profile, context
        )

        return final_recommendations[:50]  # Top 50 recommendations

    async def _collaborative_filtering(self, user_id: str, user_profile: Dict,
                                     context: Dict) -> List[Dict]:
        """Collaborative filtering recommendations"""
        # Find similar users
        similar_users = await self.ml_service.find_similar_users(
            user_id, limit=100
        )

        # Get videos watched by similar users
        candidate_videos = []
        for similar_user in similar_users:
            user_videos = await self.analytics.get_recent_watches(
                similar_user["user_id"], limit=20
            )

            for video in user_videos:
                # Skip if user already watched
                if not await self.analytics.has_user_watched(user_id, video["video_id"]):
                    candidate_videos.append({
                        "video_id": video["video_id"],
                        "score": similar_user["similarity"] * video["rating"],
                        "strategy": "collaborative_filtering"
                    })

        return candidate_videos

    async def _content_based_filtering(self, user_id: str, user_profile: Dict,
                                     context: Dict) -> List[Dict]:
        """Content-based filtering recommendations"""
        # Get user's favorite content features
        favorite_categories = user_profile.get("favorite_categories", [])
        favorite_creators = user_profile.get("favorite_creators", [])

        candidate_videos = []

        # Find videos similar to user's preferences
        for category in favorite_categories:
            similar_videos = await self.ml_service.find_videos_by_features({
                "category": category,
                "min_rating": 4.0,
                "exclude_watched": user_id
            })

            for video in similar_videos:
                candidate_videos.append({
                    "video_id": video["video_id"],
                    "score": video["similarity_score"],
                    "strategy": "content_based"
                })

        return candidate_videos

    async def _trending_boost(self, user_id: str, user_profile: Dict,
                           context: Dict) -> List[Dict]:
        """Add trending videos with user preference weighting"""
        trending_videos = await self.analytics.get_trending_videos(
            time_window="24h", limit=50
        )

        candidate_videos = []
        for video in trending_videos:
            # Weight by user's category preferences
            category_preference = user_profile.get("category_weights", {}).get(
                video["category"], 0.5
            )

            candidate_videos.append({
                "video_id": video["video_id"],
                "score": video["trending_score"] * category_preference,
                "strategy": "trending"
            })

        return candidate_videos

    async def _subscription_feed(self, user_id: str, user_profile: Dict,
                               context: Dict) -> List[Dict]:
        """Get recent videos from subscribed channels"""
        subscriptions = await self.analytics.get_user_subscriptions(user_id)

        candidate_videos = []
        for channel in subscriptions:
            recent_videos = await self.analytics.get_channel_recent_videos(
                channel["channel_id"], limit=5
            )

            for video in recent_videos:
                # Higher score for more engaged subscriptions
                engagement_score = channel.get("engagement_score", 0.5)

                candidate_videos.append({
                    "video_id": video["video_id"],
                    "score": 1.0 + engagement_score,
                    "strategy": "subscription"
                })

        return candidate_videos

    async def _hybrid_ranking(self, recommendations: List[Dict],
                            user_profile: Dict, context: Dict) -> List[str]:
        """Combine and rank recommendations from multiple strategies"""

        # Group by video_id and combine scores
        video_scores = {}
        for rec in recommendations:
            video_id = rec["video_id"]
            if video_id not in video_scores:
                video_scores[video_id] = {
                    "total_score": 0,
                    "strategies": [],
                    "video_id": video_id
                }

            video_scores[video_id]["total_score"] += rec["score"]
            video_scores[video_id]["strategies"].append(rec["strategy"])

        # Apply diversity and freshness factors
        final_scores = []
        for video_id, data in video_scores.items():
            # Diversity bonus for multiple strategies
            diversity_bonus = len(set(data["strategies"])) * 0.1

            # Get video metadata for freshness calculation
            video_meta = await self.analytics.get_video_metadata(video_id)
            freshness_score = self._calculate_freshness_score(video_meta["upload_date"])

            final_score = data["total_score"] + diversity_bonus + freshness_score

            final_scores.append({
                "video_id": video_id,
                "final_score": final_score
            })

        # Sort by final score
        final_scores.sort(key=lambda x: x["final_score"], reverse=True)

        return [item["video_id"] for item in final_scores]

    def _calculate_freshness_score(self, upload_date: datetime) -> float:
        """Calculate freshness score based on upload date"""
        days_old = (datetime.now() - upload_date).days

        if days_old <= 1:
            return 0.5
        elif days_old <= 7:
            return 0.3
        elif days_old <= 30:
            return 0.1
        else:
            return 0.0
```

## 🗄️ Database Design

### Cassandra Schema for Scale

```cql
-- Videos table (partitioned by video_id)
CREATE TABLE videos (
    video_id text PRIMARY KEY,
    channel_id text,
    title text,
    description text,
    thumbnail_url text,
    duration_seconds int,
    status text,
    content_type text,
    view_count bigint,
    like_count bigint,
    comment_count bigint,
    upload_date timestamp,
    published_at timestamp,
    tags set<text>,
    category text,
    language text
);

-- Video files table
CREATE TABLE video_files (
    video_id text,
    quality text,
    file_id text,
    format text,
    file_size_bytes bigint,
    bitrate_kbps int,
    width int,
    height int,
    cdn_url text,
    PRIMARY KEY (video_id, quality)
);

-- User activity table (time-series data)
CREATE TABLE user_activities (
    user_id text,
    activity_date date,
    timestamp timestamp,
    activity_type text,
    video_id text,
    watch_time_seconds int,
    device_type text,
    PRIMARY KEY ((user_id, activity_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Channel subscriptions
CREATE TABLE subscriptions (
    subscriber_id text,
    channel_id text,
    subscribed_at timestamp,
    notification_enabled boolean,
    PRIMARY KEY (subscriber_id, channel_id)
);

-- Comments (partitioned by video_id)
CREATE TABLE comments (
    video_id text,
    comment_id text,
    user_id text,
    content text,
    like_count int,
    reply_count int,
    parent_comment_id text,
    created_at timestamp,
    PRIMARY KEY (video_id, created_at, comment_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- View events for analytics
CREATE TABLE view_events (
    video_id text,
    view_date date,
    timestamp timestamp,
    user_id text,
    session_id text,
    watch_time_seconds int,
    quality_changes list<text>,
    device_type text,
    location text,
    PRIMARY KEY ((video_id, view_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Trending videos (materialized view updated periodically)
CREATE TABLE trending_videos (
    time_window text,  -- 'hourly', 'daily', 'weekly'
    rank int,
    video_id text,
    view_count bigint,
    engagement_score double,
    category text,
    created_at timestamp,
    PRIMARY KEY (time_window, rank)
);
```

### Elasticsearch Schema for Search

```json
{
  "mappings": {
    "properties": {
      "video_id": {"type": "keyword"},
      "title": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "suggest": {
            "type": "completion"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "standard"
      },
      "tags": {
        "type": "keyword"
      },
      "channel_id": {"type": "keyword"},
      "channel_name": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"}
        }
      },
      "category": {"type": "keyword"},
      "duration_seconds": {"type": "integer"},
      "view_count": {"type": "long"},
      "like_count": {"type": "long"},
      "upload_date": {"type": "date"},
      "transcript": {
        "type": "text",
        "analyzer": "standard"
      },
      "thumbnail_url": {"type": "keyword"},
      "language": {"type": "keyword"},
      "age_restriction": {"type": "boolean"}
    }
  },
  "settings": {
    "number_of_shards": 10,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "video_analyzer": {
          "tokenizer": "standard",
          "filter": ["lowercase", "stop", "snowball"]
        }
      }
    }
  }
}
```

## 📊 Analytics and Monitoring

```python
class AnalyticsService:
    def __init__(self, bigquery_client, redis_client):
        self.bq = bigquery_client
        self.redis = redis_client

    async def record_view_event(self, event: Dict):
        """Record detailed view event for analytics"""
        # Real-time metrics update
        await self.redis.incr(f"video_views:{event['video_id']}:today")
        await self.redis.incr(f"channel_views:{event['channel_id']}:today")

        # Stream to BigQuery for detailed analytics
        await self.bq.insert_rows_json(
            'analytics.view_events',
            [event]
        )

        # Update trending calculations
        await self._update_trending_score(event['video_id'], event)

    async def get_video_analytics(self, video_id: str, time_range: str = "7d") -> Dict:
        """Get comprehensive video analytics"""
        query = f"""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as views,
            SUM(watch_time_seconds) as total_watch_time,
            AVG(watch_time_seconds) as avg_watch_time,
            COUNT(DISTINCT user_id) as unique_viewers,
            COUNTIF(watch_time_seconds >= duration_seconds * 0.8) as completed_views
        FROM `analytics.view_events`
        WHERE video_id = @video_id
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {time_range})
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        """

        results = await self.bq.query(query, {"video_id": video_id})

        return {
            "daily_stats": list(results),
            "total_views": sum(row["views"] for row in results),
            "total_watch_time": sum(row["total_watch_time"] for row in results),
            "average_view_duration": sum(row["avg_watch_time"] for row in results) / len(results),
            "unique_viewers": sum(row["unique_viewers"] for row in results)
        }

    async def get_real_time_metrics(self) -> Dict:
        """Get real-time platform metrics"""
        # Get current concurrent viewers
        concurrent_viewers = await self.redis.get("concurrent_viewers") or 0

        # Get hourly stats
        current_hour = datetime.now().strftime("%Y%m%d%H")
        hourly_views = await self.redis.get(f"platform_views:{current_hour}") or 0
        hourly_uploads = await self.redis.get(f"platform_uploads:{current_hour}") or 0

        return {
            "concurrent_viewers": int(concurrent_viewers),
            "hourly_views": int(hourly_views),
            "hourly_uploads": int(hourly_uploads),
            "top_videos": await self._get_trending_videos("1h"),
            "platform_health": await self._get_platform_health()
        }

    async def _get_platform_health(self) -> Dict:
        """Get platform health metrics"""
        return {
            "video_processing_queue_size": await self.redis.llen("video_processing_queue"),
            "avg_processing_time_minutes": await self.redis.get("avg_processing_time") or 10,
            "cdn_cache_hit_rate": await self.redis.get("cdn_cache_hit_rate") or 0.85,
            "search_response_time_ms": await self.redis.get("search_response_time") or 50
        }
```

## ✅ Knowledge Check

After studying this design, you should understand:

- [ ] Global video streaming architecture and CDN distribution
- [ ] Video processing pipeline with multiple quality transcoding
- [ ] Search and recommendation systems at scale
- [ ] Real-time analytics and trending algorithms
- [ ] Database design for video metadata and user interactions
- [ ] Adaptive bitrate streaming and video optimization
- [ ] Content delivery and edge server management
- [ ] Scalability patterns for billions of users

## 🔄 Next Steps

- Study content recommendation algorithms in detail
- Learn about video compression and encoding techniques
- Explore real-time streaming protocols (WebRTC, RTMP)
- Understand content moderation and copyright detection
- Study monetization and ad insertion systems
- Learn about live streaming infrastructure
- Explore global content distribution strategies
- Practice designing video-heavy applications