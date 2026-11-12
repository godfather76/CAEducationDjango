from django.db import models
from pgvector.django import VectorField, HnswIndex


class CharacterMemory(models.Model):
    id = models.IntegerField(primary_key=True)
    scene_context = models.TextField()
    interlocutor_line = models.TextField()
    character_response = models.TextField()
    # Nomic-embed-text outputs 768 dimensions
    embedding = VectorField(dimensions=768)

    class Meta:
        indexes = [
            HnswIndex(
                name='character_embedding_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops']
            )
        ]

    def __str__(self):
        return self.character_response[:50]