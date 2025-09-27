from django.core.cache import cache
from django.core.management.base import BaseCommand

from core.model_registry import ModelRegistry


class Command(BaseCommand):
    help = 'Initialize model registry and clear converter cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear converter cache',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            return self._clear_cache()

        # Default action: initialize models
        return self._initialize_models()

    def _initialize_models(self):
        self.stdout.write("Initializing model registry...")
        ModelRegistry.initialize()

        self.stdout.write(
            self.style.SUCCESS(
                "✓ Model registry initialized (no Pydantic models to register)"
            )
        )

    def _clear_cache(self):
        cache.clear()
        self.stdout.write(self.style.SUCCESS("✓ Cache cleared successfully"))
