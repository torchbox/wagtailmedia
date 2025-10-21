import hmac
import json
import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from wagtailmedia.models import (
    MediaTranscodingJob,
    TranscodingJobStatus,
)
from wagtailmedia.settings import wagtailmedia_settings


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TranscodingWebhookView(View):
    """
    Webhook endpoint for receiving transcoding job status updates.

    This view handles POST requests from the AWS EventBridge API Destination to update
    job status.

    Configuration:
        WAGTAILMEDIA = {
            "WEBHOOK_API_KEY": "API_KEY",  # For auth
        }

    EventBridge Payload Format:
        {
            'version': '0',
            'id': 'UUID',
            'detail-type': 'MediaConvert Job State Change',
            'source': 'aws.mediaconvert',
            'account': 'ACCOUNT_ID',
            'time': '1970-01-01T00:00:00Z',
            'region': 'eu-west-2',
            'resources': ['arn:aws:mediaconvert:eu-west-2:ACCOUNT_ID:jobs/JOB_ID'],
            'detail': {
                'timestamp': 0,
                'accountId': 'ACCOUNT_ID',
                'queue': 'arn:aws:mediaconvert:eu-west-2:182186043439:queues/Default',
                'jobId': 'JOB_ID',
                'status': 'PROGRESSING/COMPLETE/ERROR',
                'userMetadata': {}
                'outputGroupDetails': [{
                    'outputDetails': [{
                        'outputFilePaths': ['s3://FILE_PATH'],
                        'durationInMs': 0,
                        'videoDetails': {
                            'widthInPx': 0,
                            'heightInPx': 0,
                            'averageBitrate': 0
                        }
                    }],
                    'type': 'FILE_GROUP'
                }],
                'paddingInserted': 0,
                'blackVideoDetected': 0
            }
        }
    """

    def post(self, request):
        """Handle POST requests with transcoding status updates."""

        # Verify authentication
        if not self._verify_api_key(request):
            logger.warning(
                "Webhook request with invalid authentication",
                extra={"remote_addr": request.META.get("REMOTE_ADDR")},
            )
            return JsonResponse({"error": "Unauthorized"}, status=401)

        # Parse request body
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Webhook received with invalid JSON")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # extract job data
        detail = payload["detail"]
        job_id = detail.get("jobId")
        job_status = detail.get("status")
        job_metadata = {}

        # When a completed MediaConvert event is sent is includes additional information
        if detail.get("outputGroupDetails"):
            job_metadata = detail.get("outputGroupDetails")[0].get("outputDetails")

        if not job_id or not job_status:
            logger.error(
                "Webhook received with missing required fields",
                extra={"payload": payload},
            )
            return JsonResponse(
                {"error": "Missing required fields: job_id and status"}, status=400
            )

        try:
            media_transcoding_job = MediaTranscodingJob.objects.get(job_id=job_id)
        except MediaTranscodingJob.DoesNotExist:
            logger.warning(
                f"Webhook received for unknown job_id: {job_id}",
                extra={"job_id": job_id},
            )
            return JsonResponse({"error": f"Job not found: {job_id}"}, status=404)

        # Map external status to internal status
        status = self._map_status(job_status)
        if not status:
            logger.error(
                f"Webhook received with invalid status: {job_status}",
                extra={"job_id": job_id, "status": job_status},
            )
            return JsonResponse({"error": f"Invalid status: {job_status}"}, status=400)

        logger.debug(
            f"Webhook received for Job ID: {job_id}, status: {job_status}, with metadata: {job_metadata}"
        )

        # If the transcoding job object is already complete, skip updating
        if media_transcoding_job.status is not TranscodingJobStatus.COMPLETE:
            self._update_transcoding_job(job_id, job_status, job_metadata)

        return JsonResponse(
            {
                "success": True,
                "job_id": job_id,
                "status": status,
            },
            status=200,
        )

    def _update_transcoding_job(self, job_id, job_status, job_metadata):
        media_transcoding_job = MediaTranscodingJob.objects.get(job_id=job_id)

        old_status = media_transcoding_job.status
        media_transcoding_job.status = job_status
        media_transcoding_job.metadata = job_metadata
        media_transcoding_job.save()

        logger.info(
            f"Updated job {job_id} status from {old_status} to {media_transcoding_job.status}",
            extra={
                "job_id": job_id,
                "old_status": old_status,
                "new_status": media_transcoding_job.status,
            },
        )

    def _verify_api_key(self, request):
        """
        Verify API Key authentication.

        Expects API key in X-API-Key header.
        """
        expected_key = wagtailmedia_settings.WEBHOOK_API_KEY

        # URL pattern shouldn't have been included but just in case fail the verification
        if not expected_key:
            return False

        provided_key = request.headers.get("X-API-Key") or request.headers.get(
            "X-Api-Key"
        )
        if not provided_key:
            return False

        # Constant-time comparison
        return hmac.compare_digest(provided_key, expected_key)

    def _map_status(self, status):
        """
        Map external service status to internal TranscodingJobStatus.

        Args:
            status: Status string from external service

        Returns:
            Internal status value or None if invalid
        """
        status_map = {
            "COMPLETE": TranscodingJobStatus.COMPLETE,
            "ERROR": TranscodingJobStatus.FAILED,
            "PROGRESSING": TranscodingJobStatus.PROGRESSING,
        }

        return status_map.get(status.upper())
