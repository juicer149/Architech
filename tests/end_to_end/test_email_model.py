# tests/end_to_end/test_email_model.py

import pytest
from tests.dummydomain.impl.email_model import Email


def test_email_success():
    e = Email("TEST@Example.Com")
    assert e.address == "test@example.com"  # GET pipeline applies lowercase


def test_email_missing_at_raises_valueerror():
    with pytest.raises(ValueError):
        Email("invalid")


def test_email_get_warning(pan, capsys):
    e = Email("a@b.com")
    with pan:
        _ = e.address
    #print("STDOUT:", capsys.readouterr().out)
    #print("STDERR:", capsys.readouterr().err)

    result = capsys.readouterr()
    assert "email_warn" in result.out.lower()


