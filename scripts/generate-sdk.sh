#!/bin/bash
set -e

echo "🔄 Starting SDK generation..."

# Step 1: Backup critical v2 files
echo "📦 Backing up critical files..."

# Backup pyproject.toml
if [ -f "tofupilot/v2/pyproject.toml" ]; then
    cp tofupilot/v2/pyproject.toml /tmp/v2-pyproject.toml.backup
    PYPROJECT_BACKUP_EXISTS=true
else
    echo "⚠️  No existing v2/pyproject.toml found"
    PYPROJECT_BACKUP_EXISTS=false
fi

# Backup error tracking files
if [ -f "tofupilot/v2/client_with_error_tracking.py" ]; then
    cp tofupilot/v2/client_with_error_tracking.py /tmp/client_with_error_tracking.backup
    CLIENT_BACKUP_EXISTS=true
else
    CLIENT_BACKUP_EXISTS=false
fi

if [ -f "tofupilot/v2/error_tracking_hooks.py" ]; then
    cp tofupilot/v2/error_tracking_hooks.py /tmp/error_tracking_hooks.backup
    HOOKS_BACKUP_EXISTS=true
else
    HOOKS_BACKUP_EXISTS=false
fi

# Backup custom __init__.py
if [ -f "tofupilot/v2/__init__.py" ]; then
    cp tofupilot/v2/__init__.py /tmp/v2-init.backup
    INIT_BACKUP_EXISTS=true
else
    INIT_BACKUP_EXISTS=false
fi

# Step 2: Remove old v2 directory and create temp directory
echo "🗑️  Removing old v2 directory..."
rm -rf tofupilot/v2
mkdir -p .tmp

# Step 3: Fetch and fix OpenAPI spec
echo "📥 Fetching OpenAPI spec from localhost..."
curl -s http://localhost:3000/api/v2/openapi.json > .tmp/openapi-raw.json

echo "🔧 Fixing OpenAPI spec for Speakeasy compatibility..."
python3 << 'PYEOF'
import json
import re

with open('.tmp/openapi-raw.json', 'r') as f:
    spec = json.load(f)

# Fix 1: Replace references to error.X with ErrorX format before removing
spec_str = json.dumps(spec)
error_refs = {
    '#/components/schemas/error.BAD_REQUEST': '#/components/schemas/ErrorBADREQUEST',
    '#/components/schemas/error.UNAUTHORIZED': '#/components/schemas/ErrorUNAUTHORIZED',
    '#/components/schemas/error.FORBIDDEN': '#/components/schemas/ErrorFORBIDDEN',
    '#/components/schemas/error.NOT_FOUND': '#/components/schemas/ErrorNOTFOUND',
    '#/components/schemas/error.CONFLICT': '#/components/schemas/ErrorCONFLICT',
    '#/components/schemas/error.UNPROCESSABLE_CONTENT': '#/components/schemas/ErrorUNPROCESSABLECONTENT',
    '#/components/schemas/error.INTERNAL_SERVER_ERROR': '#/components/schemas/ErrorINTERNALSERVERERROR',
    '#/components/schemas/error.BAD_GATEWAY': '#/components/schemas/ErrorBADGATEWAY',
    '#/components/schemas/error.PRECONDITION_FAILED': '#/components/schemas/ErrorPRECONDITIONFAILED',
}
for old_ref, new_ref in error_refs.items():
    spec_str = spec_str.replace(old_ref, new_ref)
spec = json.loads(spec_str)
print("  Replaced error schema references")

# Fix 2: Remove duplicate error schemas (error.X format - keep ErrorX format)
if 'components' in spec and 'schemas' in spec['components']:
    schemas_to_remove = [k for k in spec['components']['schemas'].keys() if k.startswith('error.')]
    for schema in schemas_to_remove:
        del spec['components']['schemas'][schema]
    print(f"  Removed {len(schemas_to_remove)} duplicate error schemas")

# Fix 3: Add ErrorPRECONDITIONFAILED schema if it doesn't exist
if 'components' in spec and 'schemas' in spec['components']:
    if 'ErrorPRECONDITIONFAILED' not in spec['components']['schemas']:
        spec['components']['schemas']['ErrorPRECONDITIONFAILED'] = {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': 'The error message',
                    'example': 'Precondition failed',
                },
                'code': {
                    'type': 'string',
                    'description': 'The error code',
                    'example': 'PRECONDITION_FAILED',
                },
                'issues': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                        },
                        'required': ['message'],
                    },
                    'description': 'An array of issues that were responsible for the error',
                    'example': [],
                },
            },
            'required': ['message', 'code'],
            'description': 'Precondition failed error',
        }
        print("  Added ErrorPRECONDITIONFAILED schema")

# Fix 2: Remove x-access fields (they contain "type" which conflicts with JSON Schema)
# x-access is for documentation badges, not needed for SDK generation
def remove_x_access(obj):
    if isinstance(obj, dict):
        if 'x-access' in obj:
            del obj['x-access']
        for v in obj.values():
            remove_x_access(v)
    elif isinstance(obj, list):
        for v in obj:
            remove_x_access(v)

remove_x_access(spec)
print("  Removed x-access fields")

# Fix 5: Convert type: "null" to nullable pattern (OpenAPI 3.0 compatibility)
# In OpenAPI 3.0, type can't be "null", you need to use nullable: true
def fix_null_types(obj):
    if isinstance(obj, dict):
        # Handle oneOf/anyOf with type: "null"
        for key in ['oneOf', 'anyOf']:
            if key in obj and isinstance(obj[key], list):
                # Remove type: "null" items and add nullable: true to remaining type
                has_null = False
                non_null_items = []
                for item in obj[key]:
                    if isinstance(item, dict) and item.get('type') == 'null':
                        has_null = True
                    else:
                        non_null_items.append(item)

                if has_null and len(non_null_items) == 1:
                    # Replace oneOf/anyOf with the single non-null type + nullable
                    single_type = non_null_items[0]
                    del obj[key]
                    obj.update(single_type)
                    obj['nullable'] = True
                elif has_null:
                    obj[key] = non_null_items
                    obj['nullable'] = True

        for v in obj.values():
            fix_null_types(v)
    elif isinstance(obj, list):
        for v in obj:
            fix_null_types(v)

fix_null_types(spec)
print("  Fixed null type patterns")

# Fix 3: Remove examples that have "type" field with non-schema values
def remove_problematic_examples(obj, path=""):
    if isinstance(obj, dict):
        if 'example' in obj:
            ex = obj['example']
            # Check if example contains objects with problematic "type" values
            def has_problematic_type(val):
                if isinstance(val, dict):
                    if 'type' in val and val['type'] not in ['array', 'boolean', 'integer', 'number', 'object', 'string', None]:
                        return True
                    for v in val.values():
                        if has_problematic_type(v):
                            return True
                elif isinstance(val, list):
                    for v in val:
                        if has_problematic_type(v):
                            return True
                return False

            if has_problematic_type(ex):
                del obj['example']

        for k, v in list(obj.items()):
            remove_problematic_examples(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            remove_problematic_examples(v, f"{path}[{i}]")

remove_problematic_examples(spec)
print("  Removed problematic examples")

# Fix 4: Change security scheme from 'http' to 'apiKey' (Speakeasy compatibility)
if 'components' in spec and 'securitySchemes' in spec['components']:
    sec = spec['components']['securitySchemes'].get('api_key')
    if sec and sec.get('type') == 'http':
        spec['components']['securitySchemes']['api_key'] = {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'API key for authentication. Use format: Bearer YOUR_API_KEY'
        }
        print("  Fixed security scheme type")

# Fix 5: Add 401 Unauthorized to all operations that don't have it
if 'paths' in spec:
    operations_updated = 0
    for path, methods in spec['paths'].items():
        for method, operation in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete'] and isinstance(operation, dict):
                if 'responses' in operation and '401' not in operation['responses']:
                    operation['responses']['401'] = {
                        'description': 'Unauthorized',
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': '#/components/schemas/ErrorUNAUTHORIZED'
                                }
                            }
                        }
                    }
                    operations_updated += 1
    print(f"  Added 401 response to {operations_updated} operations")

with open('.tmp/openapi-fixed.json', 'w') as f:
    json.dump(spec, f, indent=2)

print("✅ OpenAPI spec fixed successfully")
PYEOF

# Step 4: Generate SDK using the fixed spec
echo "🚀 Generating SDK with Speakeasy..."
cd .tmp
speakeasy generate sdk -s openapi-fixed.json -l python -o .
cd ..

# Step 5: Move generated SDK to final location
echo "📁 Moving generated SDK..."
mv .tmp/src/tofupilot/v2 tofupilot/v2

# Step 6: Clean up temp directory
rm -rf .tmp

# Step 7: Restore all backed up files
echo "📦 Restoring backed up files..."

# Restore pyproject.toml
if [ "$PYPROJECT_BACKUP_EXISTS" = true ]; then
    echo "📦 Restoring v2/pyproject.toml..."
    cp /tmp/v2-pyproject.toml.backup tofupilot/v2/pyproject.toml
    rm /tmp/v2-pyproject.toml.backup
else
    echo "⚠️  Creating default v2/pyproject.toml..."
    cat > tofupilot/v2/pyproject.toml << 'EOF'
[project]
name = "tofupilot-v2"
version = "0.7.3"
description = "TofuPilot v2 Speakeasy-generated SDK client"
authors = [
    { name = "TofuPilot Team", email = "hello@tofupilot.com" },
    { name = "Speakeasy" }
]
readme = "../../README.md"
license = { text = "MIT" }
requires-python = ">=3.9.2"

dependencies = [
    "httpcore>=1.0.9",
    "httpx>=0.28.1",
    "pydantic>=2.11.2",
    "posthog>=3.0.0",
]

[build-system]
requires = ["setuptools>=50.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["tofupilot.v2"]
include-package-data = true

[tool.setuptools.package-data]
"*" = ["py.typed"]
EOF
fi

# Restore error tracking files
if [ "$CLIENT_BACKUP_EXISTS" = true ]; then
    echo "📦 Restoring client_with_error_tracking.py..."
    cp /tmp/client_with_error_tracking.backup tofupilot/v2/client_with_error_tracking.py
    rm /tmp/client_with_error_tracking.backup
fi

if [ "$HOOKS_BACKUP_EXISTS" = true ]; then
    echo "📦 Restoring error_tracking_hooks.py..."
    cp /tmp/error_tracking_hooks.backup tofupilot/v2/error_tracking_hooks.py
    rm /tmp/error_tracking_hooks.backup
fi

# Restore custom __init__.py or create one
if [ "$INIT_BACKUP_EXISTS" = true ]; then
    echo "📦 Restoring custom __init__.py..."
    cp /tmp/v2-init.backup tofupilot/v2/__init__.py
    rm /tmp/v2-init.backup
else
    echo "🔧 Creating error tracking enabled __init__.py..."
    cat > tofupilot/v2/__init__.py << 'EOF'
"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from ._version import (
    __title__,
    __version__,
    __openapi_doc_version__,
    __gen_version__,
    __user_agent__,
)
# Import the error tracking enhanced client by default
from .client_with_error_tracking import TofuPilotWithErrorTracking as TofuPilot
# Still export the base SDK for those who want it
from .sdk import TofuPilot as TofuPilotBase
from .sdkconfiguration import *


VERSION: str = __version__
OPENAPI_DOC_VERSION = __openapi_doc_version__
SPEAKEASY_GENERATOR_VERSION = __gen_version__
USER_AGENT = __user_agent__

# Export both versions
__all__ = [
    "TofuPilot",  # Default with error tracking
    "TofuPilotBase",  # Base without error tracking
    # Version info
    "VERSION",
    "OPENAPI_DOC_VERSION",
    "SPEAKEASY_GENERATOR_VERSION",
    "USER_AGENT",
]
EOF
fi

echo "✅ SDK generation complete with error tracking preserved!"
