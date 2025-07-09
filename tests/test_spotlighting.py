import base64
import pytest

from spotlighting.defenses import (
    delimit_content,
    datamark_content,
    encode_content_base64,
    encode_hex,
    encode_layered,
    Spotlighter,
)

def test_delimit_content_default():
    s = "hello world"
    assert delimit_content(s) == "«hello world»"

def test_datamark_content_custom_marker():
    s = "one two   three"
    # replace whitespace sequences with custom marker
    assert datamark_content(s, marker="^") == "one^two^three"

def test_encode_content_base64_roundtrip():
    s = "radar"
    encoded = encode_content_base64(s)
    decoded = base64.b64decode(encoded).decode("utf-8")
    assert decoded == s

def test_encode_hex_roundtrip():
    s = "radar"
    encoded = encode_hex(s)
    decoded = bytes.fromhex(encoded).decode("utf-8")
    assert decoded == s

def test_encode_layered_roundtrip():
    s = "radar"
    layered = encode_layered(s)
    # First hex-decode to get base64, then base64-decode to get original
    b64 = bytes.fromhex(layered).decode("utf-8")
    decoded = base64.b64decode(b64).decode("utf-8")
    assert decoded == s

def test_rot13_roundtrip():
    s = "Hello, World!"
    spot = Spotlighter(method="rot13")
    encoded = spot.process(s)
    decoded = spot.process(encoded)
    assert decoded == s

def test_binary_roundtrip():
    s = "A"
    spot = Spotlighter(method="binary")
    bits = spot.process(s)
    # parse bits back to bytes
    data = bytes(int(b, 2) for b in bits.split())
    assert data.decode("utf-8") == s

@pytest.mark.parametrize("method, func, opts", [
    ("delimit", delimit_content, {}),
    ("datamark", lambda txt: datamark_content(txt, marker="*"), {"marker": "*"}),
    ("base64", encode_content_base64, {}),
    ("rot13", lambda txt: Spotlighter(method="rot13").process(txt), {}),
    ("binary", lambda txt: Spotlighter(method="binary").process(txt), {}),
    ("layered", encode_layered, {}),
])
def test_spotlighter_matches_direct(method, func, opts):
    s = "test content"
    # Instantiate Spotlighter with method and options
    spot = Spotlighter(method=method, **opts)
    processed = spot.process(s)
    direct = func(s)
    assert processed == direct

def test_spotlighter_unknown_method():
    spot = Spotlighter(method="unknown")
    with pytest.raises(ValueError):
        spot.process("foo")import pytest
from spotlighting.defenses import Spotlighter, encode_layered

# Test data
TEST_TEXT = "This is a test."
SIMPLE_TEXT = "test"

# --- Tests for standalone functions used by Spotlighter ---

def test_encode_layered():
    """Tests the layered encoding (Base64 then hex)."""
    text = "hello"
    # echo -n "hello" | base64 -> aGVsbG8=
    # echo -n "aGVsbG8=" | xxd -p -c 256 -> 614756736247383d
    expected = "614756736247383d"
    assert encode_layered(text) == expected

# --- Tests for Spotlighter class ---

class TestSpotlighter:
    def test_delimit_default(self):
        """Tests delimit with default delimiters."""
        spotlighter = Spotlighter(method='delimit')
        assert spotlighter.process(TEST_TEXT) == f"«{TEST_TEXT}»"

    def test_delimit_custom(self):
        """Tests delimit with custom delimiters."""
        spotlighter = Spotlighter(method='delimit', start='[[', end=']]')
        assert spotlighter.process(TEST_TEXT) == f"[[{TEST_TEXT}]]"

    def test_datamark_custom_marker(self):
        """Tests datamark with a custom marker and whitespace stripping."""
        spotlighter = Spotlighter(method='datamark', marker='_')
        assert spotlighter.process("  leading and trailing spaces  ") == "leading_and_trailing_spaces"

    def test_datamark_default_marker(self, monkeypatch):
        """Tests datamark with the default random marker."""
        # Mock random marker generation for predictability
        monkeypatch.setattr('random.randint', lambda a, b: 0xE000)
        spotlighter = Spotlighter(method='datamark')
        expected_marker = chr(0xE000)
        assert spotlighter.process(TEST_TEXT) == f"This{expected_marker}is{expected_marker}a{expected_marker}test."

    def test_base64_encoding(self):
        """Tests base64 encoding."""
        spotlighter = Spotlighter(method='base64')
        assert spotlighter.process(SIMPLE_TEXT) == "dGVzdA=="

    def test_rot13_encoding(self):
        """Tests rot13 encoding."""
        spotlighter = Spotlighter(method='rot13')
        assert spotlighter.process("Hello World") == "Uryyb Jbeyq"
        assert spotlighter.process("Uryyb Jbeyq") == "Hello World"

    def test_binary_encoding(self):
        """Tests binary encoding."""
        spotlighter = Spotlighter(method='binary')
        # 'test' -> 116 101 115 116 -> 01110100 01100101 01110011 01110100
        expected = "01110100 01100101 01110011 01110100"
        assert spotlighter.process(SIMPLE_TEXT) == expected

    def test_layered_encoding(self):
        """Tests layered encoding via Spotlighter."""
        spotlighter = Spotlighter(method='layered')
        assert spotlighter.process("hello") == "614756736247383d"

    def test_unknown_method_raises_error(self):
        """Tests that an unknown method raises a ValueError."""
        with pytest.raises(ValueError, match="Unknown spotlighting method: invalid_method"):
            spotlighter = Spotlighter(method='invalid_method')
            spotlighter.process(TEST_TEXT)

    def test_empty_string_input(self):
        """Tests various methods with an empty string."""
        # Delimit
        spotlighter_delimit = Spotlighter(method='delimit')
        assert spotlighter_delimit.process("") == "«»"
        # Base64
        spotlighter_b64 = Spotlighter(method='base64')
        assert spotlighter_b64.process("") == ""
        # Layered
        spotlighter_layered = Spotlighter(method='layered')
        assert spotlighter_layered.process("") == ""
        # Binary
        spotlighter_binary = Spotlighter(method='binary')
        assert spotlighter_binary.process("") == ""
        # Datamark
        spotlighter_datamark = Spotlighter(method='datamark')
        assert spotlighter_datamark.process("") == ""
        # rot13
        spotlighter_rot13 = Spotlighter(method='rot13')
        assert spotlighter_rot13.process("") == ""
