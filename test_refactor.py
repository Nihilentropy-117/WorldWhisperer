#!/usr/bin/env python3
"""
Test script to verify the refactored WorldWhisperer system.
Tests local embeddings and OpenRouter integration without running the full program.
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test that environment variables are configured correctly"""
    print("=" * 60)
    print("TEST 1: Environment Configuration")
    print("=" * 60)

    load_dotenv()

    required_vars = [
        'openrouter_api_key',
        'chromadb_collection_name',
        'chromadb_path'
    ]

    optional_vars = [
        'openrouter_model',
        'local_embed_model',
        'top_k',
        'chromadb_context_limit'
    ]

    print("\n✓ Checking required variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask API key for security
            if 'key' in var.lower():
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"  ✅ {var} = {display_value}")
        else:
            print(f"  ❌ {var} = NOT SET")
            return False

    print("\n✓ Checking optional variables (using defaults if not set):")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value}")
        else:
            print(f"  ⚠️  {var} = (using default)")

    return True


def test_imports():
    """Test that all required packages can be imported"""
    print("\n" + "=" * 60)
    print("TEST 2: Package Imports")
    print("=" * 60 + "\n")

    packages = {
        'sentence_transformers': 'SentenceTransformer',
        'chromadb': 'PersistentClient',
        'tiktoken': 'get_encoding',
        'requests': 'post',
        'pandas': 'DataFrame',
        'tqdm': 'tqdm'
    }

    all_good = True
    for package, component in packages.items():
        try:
            module = __import__(package)
            if hasattr(module, component) or '.' in component:
                print(f"  ✅ {package}")
            else:
                print(f"  ⚠️  {package} (imported but {component} not found)")
        except ImportError as e:
            print(f"  ❌ {package} - {e}")
            all_good = False

    return all_good


def test_local_embedding():
    """Test local embedding model"""
    print("\n" + "=" * 60)
    print("TEST 3: Local Embedding Model")
    print("=" * 60 + "\n")

    try:
        from sentence_transformers import SentenceTransformer

        model_name = os.getenv('local_embed_model', 'all-MiniLM-L6-v2')
        print(f"Loading model: {model_name}")
        print("(First run will download the model, please wait...)\n")

        model = SentenceTransformer(model_name)
        print(f"  ✅ Model loaded successfully")

        # Test embedding
        test_text = "The ancient wizard cast a powerful spell."
        print(f"\n  Testing with: '{test_text}'")
        embedding = model.encode([test_text], show_progress_bar=False)

        print(f"  ✅ Embedding created")
        print(f"     Dimension: {len(embedding[0])}")
        print(f"     First 5 values: {embedding[0][:5]}")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_openrouter_connection():
    """Test OpenRouter API connection"""
    print("\n" + "=" * 60)
    print("TEST 4: OpenRouter API Connection")
    print("=" * 60 + "\n")

    try:
        import requests

        api_key = os.getenv('openrouter_api_key')
        if not api_key:
            print("  ❌ OPENROUTER_API_KEY not set")
            return False

        # Test with a minimal request
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Check available models (doesn't cost credits)
        response = requests.get(
            'https://openrouter.ai/api/v1/models',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("  ✅ Successfully connected to OpenRouter")
            models = response.json()
            print(f"  ✅ Found {len(models.get('data', []))} available models")

            # Check if user's selected model is available
            selected_model = os.getenv('openrouter_model', 'anthropic/claude-3.5-sonnet')
            model_ids = [m['id'] for m in models.get('data', [])]

            if selected_model in model_ids:
                print(f"  ✅ Selected model '{selected_model}' is available")
            else:
                print(f"  ⚠️  Selected model '{selected_model}' not found in available models")
                print(f"      You may need to update your model selection")

            return True
        else:
            print(f"  ❌ API Error: {response.status_code}")
            print(f"     {response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def test_chromadb():
    """Test ChromaDB initialization"""
    print("\n" + "=" * 60)
    print("TEST 5: ChromaDB Initialization")
    print("=" * 60 + "\n")

    try:
        import chromadb

        chromadb_path = os.getenv('chromadb_path', './chromadb')
        collection_name = os.getenv('chromadb_collection_name', 'world_whisper_collection')

        print(f"  Testing ChromaDB at: {chromadb_path}")
        client = chromadb.PersistentClient(path=chromadb_path)
        print(f"  ✅ ChromaDB client initialized")

        # Try to get or create collection
        collection = client.get_or_create_collection(
            name=collection_name + "_test",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"  ✅ Test collection created/accessed")

        # Clean up test collection
        client.delete_collection(name=collection_name + "_test")
        print(f"  ✅ Test collection cleaned up")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("WorldWhisperer Refactor Test Suite")
    print("=" * 60)

    load_dotenv()

    tests = [
        ("Environment Configuration", test_environment),
        ("Package Imports", test_imports),
        ("Local Embedding Model", test_local_embedding),
        ("OpenRouter API Connection", test_openrouter_connection),
        ("ChromaDB Initialization", test_chromadb)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60 + "\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  🎉 All tests passed! System is ready to use.")
        print("\n  Next steps:")
        print("    1. Ensure your Notes directory is set up")
        print("    2. Run: python main.py")
        print("    3. Answer 'y' to update ChromaDB")
    else:
        print("\n  ⚠️  Some tests failed. Please fix the issues above.")
        print("\n  Common fixes:")
        print("    - Install missing packages: pip install -r requirements.txt")
        print("    - Set up .env file: cp .env.example .env")
        print("    - Add your OpenRouter API key to .env")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
