import datetime
import json
import pytest
import re

from provtoolutils.constants import model_encoding
from provtoolutils.model import make_provstring, ActingSoftware, Activity, Entity, Machine, Organization, Person, Software
from provtoolutils.utilities import calculate_data_hash, convert_rawprov2containerprov


def test_person():
    p1 = Person()
    p2 = Person()

    assert p1.id is not None
    assert p2.id is not None
    assert p1.id == p2.id

    p2 = Person('Mackie', 'Messer')
    assert p1.id != p2.id


    gn = "Horst"
    fn = "Knilch"
    p = Person(given_name=gn, family_name=fn)

    assert p.to_prov_attr()['prov:type'] == 'prov:Person'
    assert p.to_prov_attr()['person:givenName'] == gn
    assert p.to_prov_attr()['person:familyName'] == fn
    assert p.to_prov_attr()['prov:label'] is not None
    assert p.to_prov_attr()['prov:label'] == gn + ' ' + fn


    p1 = Person(given_name="Horsti", family_name="Knilchi")
    Person(given_name="Horst", family_name="Knilch", acted_on_behalf_of=p1)


def test_machine():
    m1 = Machine()
    m2 = Machine()

    assert m1.id is not None
    assert m2.id is not None
    assert m1.id == m2.id

    m2 = Machine('Robot 42')
    assert m1.id != m2.id

    assert m2.to_prov_attr()['prov:type'] == 'provtool:Machine'
    assert m2.to_prov_attr()['prov:label'] is not None
    assert m2.to_prov_attr()['prov:label'] == 'Robot 42'

    p1 = Person(given_name="Horsti", family_name="Knilchi")
    Machine('Robot 42', acted_on_behalf_of=p1)

    entityname = 'testdatensatz'
    a = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2019, 6, 1, 12, 34, 13, tzinfo=datetime.timezone.utc), 'here',
                 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])

    make_provstring(entityname, Entity.FILE, m2, a, "")

def test_provdata_generation():
    entityname = 'testdatensatz'

    p = Person(given_name="Mäx", family_name="Müstermann")
    author = ActingSoftware(acted_on_behalf_of=p, creator="The python software team",
                            version="42.13", location="http://test.test.de", label="Testsoftware")

    a = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2019, 6, 1, 12, 34, 13, tzinfo=datetime.timezone.utc), 'here',
                 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])

    datab = ''.encode(model_encoding)
    datahash = calculate_data_hash(datab)
    provb = make_provstring(entityname, Entity.FILE, author, a, datahash)
    prov = convert_rawprov2containerprov(provb)
    provn = json.loads(prov)

    entityid = calculate_data_hash(provb)
    assert calculate_data_hash(provb) in provn['entity']

    assert re.match('.*Müstermann.*', prov)

    assert len(provn['entity']) == 1
    assert provn['entity'][entityid]['prov:label'] == entityname
    assert provn['entity'][entityid]['prov:type'] == 'File'

    assert provn['activity'][a.id]['prov:startTime'] == a.start_time.isoformat()
    assert provn['activity'][a.id]['prov:endTime'] == a.end_time.isoformat()
    assert provn['activity'][a.id]['prov:location'] == a.location
    assert provn['activity'][a.id]['provtool:means'] == a.means

    assert len(provn['used'].values()) == 2
    usagelist = []
    for u in provn['used'].values():
        assert u['prov:activity'] == a.id
        usagelist.append(u['prov:entity'])
    assert "1" in usagelist
    assert "2" in usagelist

    assert provn['agent'][p.id]['prov:type'] == 'prov:Person'
    assert provn['agent'][p.id]['person:givenName'] == p.given_name
    assert provn['agent'][p.id]['person:familyName'] == p.family_name

    assert provn['agent'][author.id]['prov:type'] == 'prov:SoftwareAgent'
    assert provn['agent'][author.id]['creative:creator'] == author.creator
    assert provn['agent'][author.id]['software:softwareVersion'] == author.version
    assert provn['agent'][author.id]['prov:location'] == author.location
    assert provn['agent'][author.id]['prov:label'] == author.label

    assert len(provn['actedOnBehalfOf'].values()) == 1
    assert next(iter(provn['actedOnBehalfOf'].values()))['prov:delegate'] == author.id
    assert next(iter(provn['actedOnBehalfOf'].values()))['prov:responsible'] == p.id


def test_software():
    url = "http://test.test.de"
    creator = "The python software team"
    lic = "MIT"
    vers = "42.13"

    s1 = ActingSoftware(acted_on_behalf_of=Person(given_name="Horst", family_name="Knilch"), creator=creator,
                        version=vers, location=url, label="Testsoftware")
    s2 = ActingSoftware(acted_on_behalf_of=Person(given_name="Horst", family_name="Knilch"), creator=creator,
                        version=vers, location=url, label="Testsoftware")

    assert s1.id is not None
    assert s2.id is not None
    assert s1.id == s2.id

    s2 = ActingSoftware(acted_on_behalf_of=Person(given_name="Horst", family_name="Knilch"), creator=creator,
                        version=vers, location=url, label="Testsoftware2")
    assert s1.id != s2.id

    s1 = ActingSoftware(acted_on_behalf_of=Person(given_name="Horst", family_name="Knilch"), creator=creator,
                        version=vers, location=url, label="Testsoftware")
    ActingSoftware(acted_on_behalf_of=s1, creator=creator, version=vers, location=url,
                   label="Testsoftware")

    s = ActingSoftware(acted_on_behalf_of=Person(given_name="Horst", family_name="Knilch"), creator=creator,
                       version=vers, location=url, label="Testsoftware")

    assert s.to_prov_attr()['prov:type'] == 'prov:SoftwareAgent'
    assert s.to_prov_attr()['prov:location'] == url
    assert s.to_prov_attr()['creative:creator'] == creator
    assert s.to_prov_attr()['software:softwareVersion'] == vers
    assert s.to_prov_attr()['prov:label'] == "Testsoftware"

    p = Person(given_name="Horst", family_name="Knilch")
    s1 = Software(creator=creator, version=vers, url=url, label="Testsoftware")
    ActingSoftware(acted_on_behalf_of=p, creator=creator, version=vers,
                   location=url, label="Testsoftware")


def test_activity():
    label = 'Testaktivität'
    means = 'Diese Aktivitaet dient zum testen'
    location = 'here'
    a = Activity(datetime.datetime.now(datetime.timezone.utc), datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(5), location, label, means)

    assert a.to_prov_attr()['prov:location'] == location
    assert a.to_prov_attr()['provtool:means'] == means
    assert a.to_prov_attr()['prov:label'] == label

    a1_start = datetime.datetime.now(datetime.timezone.utc)
    a1_end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(5)
    a1_location = 'here'
    a1_label = 'Testaktivität'
    a1_means = 'Diese Aktivitaet dient zum testen'
    a1_used = ["1", "2", "3"]
    a1 = Activity(a1_start, a1_end, a1_location, a1_label, a1_means, a1_used)

    a2 = Activity(datetime.datetime.now(datetime.timezone.utc), datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(5), 'here',
                  'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2", "3"])

    assert a1.id != a2.id

    a3 = Activity(datetime.datetime.now(datetime.timezone.utc), datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(5), 'here',
                  'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2", "3"],
                  additional_props={'Notes': 'During the run, 999 of 1000 entities were filtered out to cencentrate on the high quality ones'})
    assert 'Notes' in a3.to_prov_attr()

    activity_json = f'{{"id": "{a1.id}", "start_time": "{datetime.datetime.strftime(a1_start, "%Y-%m-%dT%H:%M:%S%z")}", "end_time": "{datetime.datetime.strftime(a1_end, "%Y-%m-%dT%H:%M:%S%z")}", "location": "{a1_location}", "label": "{a1_label}", "means": "{a1_means}", "used": ["1", "2", "3"]}}'
    a1_dict = json.loads(a1.to_json())
    expected = json.loads(activity_json)
    assert a1_dict == expected

    assert Activity.from_json(activity_json).__dict__ == a1.__dict__


def test_activity_with_different_usage_order():
    label = 'Testaktivität'
    means = 'Diese Aktivitaet dient zum testen'
    location = 'here'
    a = Activity(datetime.datetime.now(datetime.timezone.utc), datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(5), location, label, means)

    assert a.to_prov_attr()['prov:location'] == location
    assert a.to_prov_attr()['provtool:means'] == means
    assert a.to_prov_attr()['prov:label'] == label

    a_start = datetime.datetime.now(datetime.timezone.utc)
    a_end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(5)
    a1 = Activity(a_start, a_end, 'here', 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2", "3"], generate_uuid=False)

    a2 = Activity(a_start, a_end, 'here', 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["3", "2", "1"], generate_uuid=False)

    p = Person(given_name="Horst", family_name="Knilch")
    author = ActingSoftware(acted_on_behalf_of=p, creator="The python software team",
                            version="42.13", location="http://test.test.de", label="Testsoftware")
    datab = "".encode()
    datahash = calculate_data_hash(datab)
    rawprov1 = make_provstring("test", Entity.FILE, author, a1, datahash)
    entityid1 = calculate_data_hash(rawprov1)
    containerprov1 = convert_rawprov2containerprov(rawprov1)
    rawprov2 = make_provstring("test", Entity.FILE, author, a2, datahash)
    entityid2 = calculate_data_hash(rawprov2)
    containerprov2 = convert_rawprov2containerprov(rawprov2)

    assert containerprov1 == containerprov2
    assert rawprov1 == rawprov2

def test_singular_agent():
    p = Person(given_name="Horst", family_name="Knilch")
    a = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2019, 6, 1, 12, 34, 13, tzinfo=datetime.timezone.utc), 'here',
                 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])
    datab = "".encode()
    make_provstring("test", Entity.FILE, p, a, calculate_data_hash(datab))


def test_pure_software_agent():
    o = Organization(name='TestOrg')
    p_alone = Person(given_name="Horst", family_name="Knilch")
    p_behalf = Person(given_name="Horst", family_name="Knilch", acted_on_behalf_of=o)
    with pytest.raises(ValueError) as e:
        s_alone = ActingSoftware(acted_on_behalf_of=None, creator=p_alone, version='', label='', location='')
    s_behalf = ActingSoftware(acted_on_behalf_of=p_alone, creator="Horst Knilch", version='', label='', location='')
    a = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2019, 6, 1, 12, 34, 13, tzinfo=datetime.timezone.utc), 'here',
                 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])
    datab = "".encode()
    datahash = calculate_data_hash(datab)

    pd = make_provstring("test", Entity.FILE, p_alone, a, datahash)
    pd = make_provstring("test", Entity.FILE, p_behalf, a, datahash)
    pd = make_provstring("test", Entity.FILE, s_behalf, a, datahash)


def test_data_hash():
    p = Person(given_name="Horst", family_name="Knilch")
    a = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2019, 6, 1, 12, 34, 13, tzinfo=datetime.timezone.utc), 'here',
                 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])
    datab = "sagadfbvadf".encode(model_encoding)
    datahash = calculate_data_hash(datab)
    rawprov = make_provstring("test", Entity.FILE, p, a, datahash)
    entityid = calculate_data_hash(rawprov)
    containerprov = convert_rawprov2containerprov(rawprov)

    assert json.loads(containerprov)['entity'][entityid]['provtool:datahash'] == datahash


def test_was_started_by():
    p = Person(given_name="Horst", family_name="Knilch")
    a1 = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), None, 'here',
                 'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])
    datab = "".encode()
    datahash = calculate_data_hash(datab)
    rawprov = make_provstring("test", Entity.FILE, p, a1, datahash)
    entityid = calculate_data_hash(rawprov)
    containerprov = convert_rawprov2containerprov(rawprov)

    assert 'wasStartedBy' not in containerprov

    a2 = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2019, 6, 1, 12, 34, 13, tzinfo=datetime.timezone.utc), 'here',
                  'Testaktivität2', 'Diese Aktivitaet dient zum testen', ["1", "2"], a1)
    rawprov = make_provstring("test", Entity.FILE, p, a2, datahash)
    entityid = calculate_data_hash(rawprov)
    containerprov = convert_rawprov2containerprov(rawprov)

    assert 'wasStartedBy' in containerprov
    # The parent activity is NOT expanded here. Reason is that otherwise the process provenance can be written only,
    # if the parent activity finished. This is a minor problem with bounded workflows but a big problem with unbounded
    # workflows which run infinitely and never end.
    # It allows furthermore, to write the provenance information as soon as the activity ends which can be way before
    # the overall process ends.

    # Expect the wasStartedBy relation to point to a1.
    expected_id = a1.id
    found = False
    for k, v in json.loads(containerprov)['wasStartedBy'].items():
        if v['prov:starter'] == a1.id:
            found = True
    assert found

    # Expect the wasStartedBy relation to point to a1 after setting the end_time of a1. It is assumed that the a1-id is
    # not changed.
    a1.end_time = datetime.datetime(2019, 6, 1, 12, 34, 13)
    assert expected_id == a1.id

    rawprov = make_provstring("test", Entity.FILE, p, a2, datahash)
    entityid = calculate_data_hash(rawprov)
    containerprov = convert_rawprov2containerprov(rawprov)
    found = False
    for k, v in json.loads(containerprov)['wasStartedBy'].items():
        if v['prov:starter'] == expected_id:
            found = True
    assert found

    # Expect the id of the overall activity a1 to be the same like before.
    rawprov = make_provstring("test", Entity.FILE, p, a1, datahash)
    entityid = calculate_data_hash(rawprov)
    containerprov = convert_rawprov2containerprov(rawprov)
    found = False
    for k, v in json.loads(containerprov)['activity'].items():
        if k == expected_id:
            found = True
    assert found


def test_ids():
    p = Person(given_name="Horst", family_name="Knilch")
    a1 = Activity(datetime.datetime(2019, 6, 1, 12, 34, 0, tzinfo=datetime.timezone.utc), None, 'here',
                  'Testaktivität', 'Diese Aktivitaet dient zum testen', ["1", "2"])
    datab = "".encode(model_encoding)
    datahash = calculate_data_hash(datab)
    rawprov = make_provstring("test", Entity.FILE, p, a1, datahash)
    entityid = calculate_data_hash(rawprov)
    containerprov = convert_rawprov2containerprov(rawprov)

    assert calculate_data_hash(rawprov) in json.loads(containerprov)['entity']

    assert 'self' in rawprov.decode(model_encoding)
    assert not 'self' in containerprov
