import rdflib
from logger import log
from pyrdfj2 import J2RDFSyntaxBuilder
from SPARQLWrapper import SPARQLWrapper, JSON
from TravHarvConfigBuilder import AssertPath
from TargetStore import TargetStore
from WebAccess import WebAccess
import os


def get_j2rdf_builder():
    template_folder = os.path.join(os.path.dirname(__file__), "pysubyt_templates")
    log.info(f"template_folder == {template_folder}")
    # init J2RDFSyntaxBuilder
    j2rdf = J2RDFSyntaxBuilder(templates_folder=template_folder)
    return j2rdf


J2RDF = get_j2rdf_builder()


class SubjPropPathAssertion:
    """
    A class to represent the assertion of all given property traversal paths for a given subject.
    """

    def __init__(
        self, subject: str, assertion_path: AssertPath, target_store: TargetStore
    ):
        self.subject = self._subject_str_check(subject)
        self.assertion_path = assertion_path
        self.current_depth = 0
        self.target_store = target_store.get_target_store()
        self.previous_bounce_depth = 0
        self.max_depth = self.assertion_path.get_max_size()
        self.assert_path()

    def _subject_str_check(self, subject):
        """
        Check if subject is a strict str , if subject is rdflib.term.URIRef , convert to str
        """
        if type(subject) == str:
            return subject
        if (
            type(subject) == rdflib.query.ResultRow
            or type(subject) == rdflib.term.URIRef
        ):
            # extract URIRef from ResultRow
            if type(subject) == rdflib.query.ResultRow:
                subject_row = subject[0]
                log.debug("Subject row: {}".format(subject_row))
                return str(subject_row)
            return str(subject)
        log.debug("Subject is of type {}".format(type(subject)))

    def assert_path(self):
        """
        Assert a property path for a given subject.
        """
        log.debug("Asserting a property path for a given subject")
        log.debug("Subject: {}".format(self.subject))
        # Implement method to assert a property path for a given subject
        while self.current_depth < self.max_depth:
            if self.current_depth > self.previous_bounce_depth:
                self._bail_out()
            self._assert_at_depth()
            self._increase_depth()

    def _assert_at_depth(self):
        """
        Assert a property path for a given subject at a given depth.
        """
        log.debug("Asserting a property path for a given subject at a given depth")
        log.debug("Depth: {}".format(self.max_depth - self.current_depth))
        SPARQLQuery = self._sparql_trajectory_check(self.max_depth - self.current_depth)
        if self.target_store.verify(SPARQLQuery):
            self._harvest_and_surface()
            return
        self.target_store.ingest(WebAccess(self.subject))

        # Implement method to assert a property path for a given subject at a given depth

    def _increase_depth(self):
        """
        Increase the depth of the property path assertion.
        """
        log.debug("Increasing the depth of the property path assertion")
        # Implement method to increase the depth of the property path assertion
        self.current_depth += 1

    def _harvest_and_surface(self):
        """
        Harvest the property path and surface back to depth 0.
        """
        log.debug("Harvesting the property path and backtracking to the previous depth")
        # Implement method to harvest the property path and backtrack to the previous depth
        self.previous_bounce_depth = self.current_depth
        self.current_depth = 0

    def _bail_out(self):
        """
        Bail out of the property path assertion.
        """
        log.debug("Bailing out of the property path assertion")
        return

    def _sparql_trajectory_check(self, depth):
        log.debug(
            "assertion_path: {}".format(self.assertion_path.get_path_for_depth(depth))
        )
