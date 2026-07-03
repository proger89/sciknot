from sciknot.catalog import load_dictionary
from sciknot.linking import link_entity


def test_exact_alias_linking():
    canonical, score = link_entity("НДС Комсомольский", load_dictionary("materials"))
    assert canonical == "Комсомольский рудный массив"
    assert score == 1.0


def test_unresolved_candidate():
    canonical, score = link_entity("совершенно другой объект", load_dictionary("materials"))
    assert canonical is None
    assert score < 1.0

