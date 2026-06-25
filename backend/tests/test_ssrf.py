"""QA-Gate: SSRF guard for outbound model-endpoint URLs."""
import pytest

from app.core import ssrf


def test_scheme_must_be_http():
    for bad in ("ftp://host/x", "file:///etc/passwd", "gopher://x", "ws://x"):
        with pytest.raises(ssrf.UnsafeUrlError):
            ssrf.validate_outbound_url(bad)


def test_blocks_cloud_metadata_and_link_local():
    # 169.254.169.254 = cloud metadata; always blocked regardless of allow_private
    with pytest.raises(ssrf.UnsafeUrlError):
        ssrf.validate_outbound_url("http://169.254.169.254/latest/meta-data/", allow_private=True)


def test_blocks_private_when_disallowed_but_allows_when_enabled():
    # loopback is allowed for local models by default …
    ssrf.validate_outbound_url("http://127.0.0.1:11434/v1", allow_private=True)
    # … but blocked when private hosts are disallowed
    with pytest.raises(ssrf.UnsafeUrlError):
        ssrf.validate_outbound_url("http://127.0.0.1:11434/v1", allow_private=False)


def test_allows_public_host():
    # public hostnames resolve to public IPs → allowed
    ssrf.validate_outbound_url("https://openrouter.ai/api/v1", allow_private=False)


def test_unresolvable_host_rejected():
    with pytest.raises(ssrf.UnsafeUrlError):
        ssrf.validate_outbound_url("http://no-such-host.invalid/v1")
