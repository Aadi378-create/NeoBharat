"""Firebase Integration Client for NeoBharat.

Provides Firestore cloud persistence with automatic fallback to a robust
thread-safe in-memory MockFirestoreClient when Firebase credentials are not
configured in the environment.

Follows the principle:
- SQLite = Authoritative Deterministic Financial Engine (customers, transactions, Guardian, decisions).
- Firestore = Cloud Application State (appointments, conversations, user preferences, sessions).

Zero hardcoded secrets. Uses environment variables:
- FIREBASE_SERVICE_ACCOUNT_KEY (path to service account JSON or raw JSON string)
- FIREBASE_PROJECT_ID
- FIREBASE_USE_MOCK (optional flag: 'true'/'1' to force mock mode in tests)
"""

import copy
import json
import logging
import os
import threading
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Global lock for thread safety in mock store
_mock_lock = threading.Lock()
_mock_db_store: Dict[str, Dict[str, Dict[str, Any]]] = {}

_firebase_app = None
_firestore_client = None


class MockDocumentSnapshot:
    """Snapshot representing a single Firestore document in the mock store."""

    def __init__(self, doc_id: str, data: Optional[Dict[str, Any]], exists: bool):
        self.id = doc_id
        self._data = copy.deepcopy(data) if data is not None else None
        self.exists = exists

    def to_dict(self) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self._data) if self._data is not None else None


class MockDocumentReference:
    """Reference to a document in the mock Firestore store."""

    def __init__(self, collection_name: str, doc_id: str, store: Dict[str, Dict[str, Dict[str, Any]]]):
        self.id = doc_id
        self.collection_name = collection_name
        self._store = store

    def get(self) -> MockDocumentSnapshot:
        with _mock_lock:
            col = self._store.get(self.collection_name, {})
            data = col.get(self.id)
            if data is None:
                return MockDocumentSnapshot(self.id, None, False)
            return MockDocumentSnapshot(self.id, data, True)

    def set(self, data: Dict[str, Any], merge: bool = False) -> None:
        with _mock_lock:
            if self.collection_name not in self._store:
                self._store[self.collection_name] = {}
            if merge and self.id in self._store[self.collection_name]:
                self._store[self.collection_name][self.id].update(copy.deepcopy(data))
            else:
                self._store[self.collection_name][self.id] = copy.deepcopy(data)

    def update(self, updates: Dict[str, Any]) -> None:
        with _mock_lock:
            col = self._store.get(self.collection_name, {})
            if self.id not in col:
                raise KeyError(f"Document {self.id} does not exist in collection {self.collection_name}")
            col[self.id].update(copy.deepcopy(updates))

    def delete(self) -> None:
        with _mock_lock:
            col = self._store.get(self.collection_name, {})
            if self.id in col:
                del col[self.id]

    def collection(self, subcollection_name: str) -> Any:
        path = f"{self.collection_name}/{self.id}/{subcollection_name}"
        return MockCollectionReference(path, self._store)


class MockQuery:
    """Mock query supporting where(), order_by(), limit(), stream()."""

    def __init__(
        self,
        collection_name: str,
        store: Dict[str, Dict[str, Dict[str, Any]]],
        filters: Optional[List[tuple]] = None,
        limit_val: Optional[int] = None,
    ):
        self.collection_name = collection_name
        self._store = store
        self._filters = filters or []
        self._limit_val = limit_val

    def where(self, field: str, op: str, value: Any) -> "MockQuery":
        new_filters = list(self._filters)
        new_filters.append((field, op, value))
        return MockQuery(self.collection_name, self._store, new_filters, self._limit_val)

    def limit(self, count: int) -> "MockQuery":
        return MockQuery(self.collection_name, self._store, self._filters, count)

    def stream(self) -> List[MockDocumentSnapshot]:
        with _mock_lock:
            col = self._store.get(self.collection_name, {})
            results: List[MockDocumentSnapshot] = []

            for doc_id, data in col.items():
                match = True
                for field, op, val in self._filters:
                    actual = data.get(field)
                    if op in ("==", "="):
                        if actual != val:
                            match = False
                            break
                    elif op == "!=":
                        if actual == val:
                            match = False
                            break
                    elif op == ">":
                        if actual is None or actual <= val:
                            match = False
                            break
                    elif op == ">=":
                        if actual is None or actual < val:
                            match = False
                            break
                    elif op == "<":
                        if actual is None or actual >= val:
                            match = False
                            break
                    elif op == "<=":
                        if actual is None or actual > val:
                            match = False
                            break
                    elif op in ("in", "IN"):
                        if actual not in val:
                            match = False
                            break
                if match:
                    results.append(MockDocumentSnapshot(doc_id, data, True))

            if self._limit_val is not None:
                results = results[: self._limit_val]

            return results


class MockCollectionReference(MockQuery):
    """Reference to a collection in the mock Firestore store."""

    def __init__(self, collection_name: str, store: Dict[str, Dict[str, Dict[str, Any]]]):
        super().__init__(collection_name, store)

    def document(self, doc_id: Optional[str] = None) -> MockDocumentReference:
        if not doc_id:
            doc_id = str(uuid.uuid4())
        return MockDocumentReference(self.collection_name, doc_id, self._store)

    def add(self, data: Dict[str, Any]) -> tuple[Any, MockDocumentReference]:
        doc_id = str(uuid.uuid4())
        ref = self.document(doc_id)
        ref.set(data)
        return (None, ref)


class MockFirestoreClient:
    """Thread-safe in-memory Firestore client for development and automated testing."""

    def __init__(self):
        self._store = _mock_db_store
        logger.info("Initialized MockFirestoreClient in local development mode.")

    def collection(self, name: str) -> MockCollectionReference:
        return MockCollectionReference(name, self._store)


def reset_mock_firestore() -> None:
    """Reset the mock store. Useful between tests."""
    with _mock_lock:
        _mock_db_store.clear()


def get_firestore_client() -> Any:
    """Obtain the active Firestore client.

    Returns the real Firestore client if credentials are configured;
    otherwise gracefully returns a thread-safe MockFirestoreClient.
    """
    global _firebase_app, _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    # Check if mock mode is forced via environment
    if os.environ.get("FIREBASE_USE_MOCK", "").lower() in ("true", "1", "yes"):
        logger.info("FIREBASE_USE_MOCK is set. Using MockFirestoreClient.")
        _firestore_client = MockFirestoreClient()
        return _firestore_client

    # Check for service account configuration
    sa_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
    project_id = os.environ.get("FIREBASE_PROJECT_ID")

    if not sa_key and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        for default_file in ("firebase-credentials.json", "serviceAccountKey.json", "config/serviceAccountKey.json"):
            if os.path.isfile(default_file):
                sa_key = default_file
                break

    if not sa_key and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.info("No Firebase credentials detected in environment. Operating in MockFirestoreClient mode.")
        _firestore_client = MockFirestoreClient()
        return _firestore_client

    # Attempt to initialize real Firebase Admin SDK
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            cred = None
            if sa_key:
                if os.path.isfile(sa_key):
                    cred = credentials.Certificate(sa_key)
                else:
                    # Parse as JSON string if not a file path
                    try:
                        key_dict = json.loads(sa_key)
                        cred = credentials.Certificate(key_dict)
                    except Exception as parse_err:
                        logger.warning("Failed to parse FIREBASE_SERVICE_ACCOUNT_KEY as JSON: %s", parse_err)
            
            if cred:
                _firebase_app = firebase_admin.initialize_app(cred, {"projectId": project_id} if project_id else None)
            else:
                _firebase_app = firebase_admin.initialize_app()

        _firestore_client = firestore.client()
        logger.info("Successfully connected to live Firebase Firestore.")
        return _firestore_client
    except Exception as e:
        logger.warning(
            "Could not initialize real Firebase Admin SDK (%s). Falling back to MockFirestoreClient.",
            e,
        )
        _firestore_client = MockFirestoreClient()
        return _firestore_client


def is_real_firebase() -> bool:
    """Check whether the active Firestore client is a live Firebase connection or MockFirestore."""
    client = get_firestore_client()
    return not isinstance(client, MockFirestoreClient)

