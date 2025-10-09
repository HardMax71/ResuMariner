import asyncio
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from neomodel import adb
from qdrant_client.http import models as qdrant_models

from core.database import QDRANT_CLIENT

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialize database connections and collections"

    def handle(self, *args, **options):
        self.stdout.write("Initializing databases...")
        asyncio.run(self._init_databases())
        self.stdout.write(self.style.SUCCESS("Database initialization complete"))

    async def _init_databases(self):
        # Initialize Neo4j
        host = settings.NEO4J_URI.replace("bolt://", "")
        connection_url = f"bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{host}"

        await adb.set_connection(url=connection_url)
        await adb.install_all_labels()
        self.stdout.write(self.style.SUCCESS(f"Neo4j connected: {host}"))

        # Initialize Qdrant collection
        collection_name = settings.QDRANT_COLLECTION

        collections = await QDRANT_CLIENT.get_collections()
        exists = any(c.name == collection_name for c in collections.collections)

        if exists:
            self.stdout.write(f"Qdrant collection {collection_name} already exists")
            return

        await QDRANT_CLIENT.create_collection(
            collection_name=collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=settings.VECTOR_SIZE,
                distance=qdrant_models.Distance.COSINE,
            ),
        )

        keyword_fields = ["uid", "name", "source", "email", "skills", "companies", "role", "location"]
        for field in keyword_fields:
            await QDRANT_CLIENT.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=qdrant_models.PayloadSchemaType.KEYWORD,
            )

        await QDRANT_CLIENT.create_payload_index(
            collection_name=collection_name,
            field_name="years_experience",
            field_schema=qdrant_models.PayloadSchemaType.INTEGER,
        )

        self.stdout.write(self.style.SUCCESS(f"Qdrant collection {collection_name} created with indices"))
