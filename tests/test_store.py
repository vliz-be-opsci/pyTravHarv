#! /usr/bin/env python
from util4tests import run_single_test
import pytest
from string import ascii_lowercase
from pytravharv.store import TargetStoreAccess, TargetStore, URITargetStore
import math
import random
from rdflib import Graph, URIRef, BNode, Literal
import datetime
from pytravharv.common import QUERY_BUILDER


@pytest.mark.usefixtures("prepopulated_target_store")
def test_select_subjects(prepopulated_target_store):
    assert (
        prepopulated_target_store is not None
    ), "can't perform test without target store"
    sparql = "SELECT ?subject ?p WHERE { ?subject ?p ?o }"
    tsa = TargetStoreAccess(prepopulated_target_store, QUERY_BUILDER)
    subjects = tsa.select_subjects(sparql)
    assert isinstance(subjects, list)
    assert len(subjects) > 0
    # Add more assertions as needed


def test_graph_to_batches():
    graph = Graph()
    groupsize = 2
    max_line = 4096 / groupsize
    stuffing = "<> <> <> . \n"
    available_len = max_line - len(stuffing)
    # Add a million triples to the graph
    cnt = 0
    for i in range(10):
        for c in ascii_lowercase:
            j = int(math.floor(random.randint(0, int(available_len)) / 3))
            element_lengths = [i, j, (int(available_len) - (int(i) + int(j)))]
            # Create the list
            elements = [URIRef(c * int(element_lengths[k])) for k in range(3)]
            graph.add((elements[0], elements[1], elements[2]))
            cnt += 1

    print(f"{len(graph)=}")
    assert (
        len(graph) == cnt
    ), "we should have not created duplicate or missing triples"
    batches = URITargetStore._graph_to_batches(graph)
    assert len(batches) > 0
    # total number of batches should be 260
    assert (
        len(batches) == cnt / groupsize
    ), f"the amount of batches should be count of all triples over groupsize"
    found_sizes = {len(grp.split("\n")) for grp in batches}
    expected_sizes = {groupsize}

    first_batch = batches[0].split("\n")
    print(f"{first_batch=}")
    # print(f"First batch split by newline: {batches[0].split('\n')}")
    assert (
        found_sizes == expected_sizes
    ), f"all batches should be of size {expected_sizes} not {found_sizes}"


@pytest.mark.usefixtures("target_store")
def test_insert(target_store):
    graph = Graph()
    context = "test_context"

    # Insert graph without context
    target_store.insert(graph)
    assert len(target_store._all) == len(graph)

    # Insert graph with context
    target_store.insert(graph, context)
    assert len(target_store._all) == len(graph)
    assert len(target_store._named_graphs[context]) == len(graph)
    assert context in target_store._admin_registry


@pytest.mark.usefixtures("target_store")
def test_lastmod_for_context(target_store):

    context = "test_context"
    target_store.insert(Graph(), context)
    lastmod = target_store.lastmod_for_context(context)

    # Add some data to the context
    target_store._admin_registry[context] = datetime.datetime.now()
    lastmod = target_store.lastmod_for_context(context)
    assert lastmod is not None, "lastmod should not be None after adding data"
    assert isinstance(
        lastmod, datetime.datetime
    ), "lastmod should be a datetime object"


@pytest.mark.usefixtures("target_store")
def test_big_insert_triple(target_store):
    graph = Graph()
    graph.parse(
        "tests/inputs/marineinfo-publication-288351.jsonld", format="json-ld"
    )
    target_store.insert(graph)

    all_triples = target_store.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

    assert len(all_triples) > 0


if __name__ == "__main__":
    run_single_test(__file__)
