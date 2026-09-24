OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Office Portal API",
        "version": "2.0.0",
        "description": "REST API for the internal Office Web Portal.",
    },
    "servers": [{"url": "/"}],
    "tags": [
        {"name": "Authentication"},
        {"name": "Files"},
        {"name": "Admin"},
    ],
    "components": {
        "securitySchemes": {
            "sessionCookie": {"type": "apiKey", "in": "cookie", "name": "session"},
        },
        "schemas": {
            "Credentials": {
                "type": "object",
                "required": ["username", "password"],
                "properties": {
                    "username": {"type": "string", "example": "admin"},
                    "password": {"type": "string", "format": "password", "example": "AdminPass123!"},
                },
            },
            "Error": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
    "paths": {
        "/api/health": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Check backend health",
                "responses": {"200": {"description": "Backend is running"}},
            }
        },
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Log in and create a session",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Credentials"}}},
                },
                "responses": {
                    "200": {"description": "Login successful"},
                    "401": {"description": "Invalid credentials"},
                    "429": {"description": "Temporarily blocked"},
                },
            }
        },
        "/api/auth/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "Destroy the current session",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Logged out"}},
            }
        },
        "/api/auth/me": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get the current user",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Current user"}},
            }
        },
        "/api/dashboard/stats": {
            "get": {
                "tags": ["Files"],
                "summary": "Get employee dashboard statistics",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Dashboard statistics"}},
            }
        },
        "/api/files/upload": {
            "post": {
                "tags": ["Files"],
                "summary": "Upload one or more files",
                "security": [{"sessionCookie": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "required": ["files"],
                                "properties": {
                                    "folder": {"type": "string", "enum": ["personal", "common"], "default": "personal"},
                                    "files": {"type": "array", "items": {"type": "string", "format": "binary"}},
                                },
                            }
                        }
                    },
                },
                "responses": {"201": {"description": "Files uploaded"}},
            }
        },
        "/api/files/personal": {
            "get": {
                "tags": ["Files"],
                "summary": "List the current user's personal files",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Personal files"}},
            }
        },
        "/api/files/common": {
            "get": {
                "tags": ["Files"],
                "summary": "List common files",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Common files"}},
            }
        },
        "/api/files/download/{file_id}": {
            "get": {
                "tags": ["Files"],
                "summary": "Download a file",
                "security": [{"sessionCookie": []}],
                "parameters": [{"name": "file_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "File download", "content": {"application/octet-stream": {}}}},
            }
        },
        "/api/files/{file_id}": {
            "delete": {
                "tags": ["Files"],
                "summary": "Delete a file",
                "security": [{"sessionCookie": []}],
                "parameters": [{"name": "file_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "File deleted"}, "403": {"description": "Not permitted"}},
            }
        },
        "/api/admin/stats": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get system statistics",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Admin statistics"}, "403": {"description": "Admin access required"}},
            }
        },
        "/api/admin/users": {
            "get": {
                "tags": ["Admin"],
                "summary": "List users",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Users"}},
            },
            "post": {
                "tags": ["Admin"],
                "summary": "Create a user",
                "security": [{"sessionCookie": []}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}},
                "responses": {"201": {"description": "User created"}},
            },
        },
        "/api/admin/users/{user_id}": {
            "put": {
                "tags": ["Admin"],
                "summary": "Activate or deactivate a user",
                "security": [{"sessionCookie": []}],
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "required": ["is_active"]}}}},
                "responses": {"200": {"description": "Status updated"}},
            },
            "delete": {
                "tags": ["Admin"],
                "summary": "Delete a user",
                "security": [{"sessionCookie": []}],
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {"200": {"description": "User deleted"}},
            },
        },
        "/api/admin/users/{user_id}/reset-password": {
            "post": {
                "tags": ["Admin"],
                "summary": "Reset a user's password",
                "security": [{"sessionCookie": []}],
                "parameters": [{"name": "user_id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "required": ["password"]}}}},
                "responses": {"200": {"description": "Password reset"}},
            }
        },
        "/api/admin/files": {
            "get": {
                "tags": ["Admin"],
                "summary": "List all files",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "All files"}},
            }
        },
        "/api/admin/logs": {
            "get": {
                "tags": ["Admin"],
                "summary": "List audit logs",
                "security": [{"sessionCookie": []}],
                "responses": {"200": {"description": "Audit logs"}},
            }
        },
    },
}
