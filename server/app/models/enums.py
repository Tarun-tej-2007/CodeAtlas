import enum

class UserRole(str, enum.Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"

class Visibility(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    INTERNAL = "INTERNAL"

class ProjectVisibility(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"



class RepositoryProvider(str, enum.Enum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET = "BITBUCKET"
    LOCAL = "LOCAL"

class RepositoryStatus(str, enum.Enum):
    PENDING = "PENDING"
    CLONING = "CLONING"
    READY = "READY"
    SYNCING = "SYNCING"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"
