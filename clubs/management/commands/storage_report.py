# Management command to monitor storage usage and costs
from django.core.management.base import BaseCommand
from django.utils import timezone
from clubs.storage_backends import StorageMetrics
import json


class Command(BaseCommand):
    help = 'Monitor storage usage and estimate costs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format'
        )
        parser.add_argument(
            '--check-migration',
            action='store_true',
            help='Check if migration to S3 is recommended'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 MotoMundo Storage Analysis Report')
        )
        self.stdout.write('=' * 50)
        
        try:
            # Get storage metrics
            metrics = StorageMetrics.estimate_monthly_costs()
            
            if options['format'] == 'json':
                self.stdout.write(json.dumps(metrics, indent=2))
            else:
                self._display_table_format(metrics)
            
            if options['check_migration']:
                self._check_migration_recommendation(metrics)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error analyzing storage: {e}')
            )

    def _display_table_format(self, metrics):
        usage = metrics['current_usage']
        
        self.stdout.write('\n📊 Current Usage:')
        self.stdout.write(f"   Total Storage: {usage['total_size_mb']} MB")
        self.stdout.write(f"   File Count: {usage['file_count']} files")
        self.stdout.write(f"   Average File Size: {usage['avg_file_size_mb']} MB")
        
        self.stdout.write('\n💰 Cost Estimates:')
        self.stdout.write(f"   Cloudinary: ${metrics['cloudinary_cost']}/month")
        self.stdout.write(f"   AWS S3: ${metrics['s3_estimated_cost']}/month")
        
        recommendation = metrics['recommendation']
        color = self.style.SUCCESS if recommendation == 'cloudinary' else self.style.WARNING
        
        self.stdout.write(f"\n🎯 Recommendation: {color(recommendation.upper())}")

    def _check_migration_recommendation(self, metrics):
        usage = metrics['current_usage']
        
        self.stdout.write('\n🔄 Migration Analysis:')
        
        # Check thresholds
        size_threshold = 20 * 1024  # 20GB in MB
        cost_savings = metrics['cloudinary_cost'] - metrics['s3_estimated_cost']
        
        if usage['total_size_mb'] > size_threshold and cost_savings > 20:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Migration to S3 recommended!"
                )
            )
            self.stdout.write(f"   Potential savings: ${cost_savings}/month")
            self.stdout.write(f"   Storage size: {usage['total_size_mb']} MB > {size_threshold} MB threshold")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ Current storage backend is optimal"
                )
            )
        
        self.stdout.write(f"\n📅 Report generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
