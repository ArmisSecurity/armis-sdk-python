from armis_sdk.entities.site import Site


def test_site_with_children():
    child = Site(id=2, name="Child Site")
    parent = Site(id=1, name="Parent Site", children=[child])
    assert len(parent.children) == 1
    assert parent.children[0].name == "Child Site"


def test_site_no_children():
    site = Site(id=1, name="HQ")
    assert site.children == []
