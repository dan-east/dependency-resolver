from ..utilities.errors import ProjectError 

class ProtocolError(ProjectError) :
    """Wraps underlying exepctions to make handling them easier for calling code."""

class FetchError(ProtocolError) :
    """Raised when fetching dependency sources fails. Wraps underlying exepctions when fetching a source using the specified protocol."""

class ResolveError(ProjectError) :
    """Raised when resolving dependencies fails. Wraps underlying exepctions to make handling them easier for calling code."""
