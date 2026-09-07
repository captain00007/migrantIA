import os
import sys
import django

# Setup Django Environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ia.ingestion.indexer import KnowledgeIndexer

if __name__ == '__main__':
    indexer = KnowledgeIndexer()
    indexer.run()
