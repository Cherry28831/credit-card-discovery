from langgraph.graph import StateGraph
from config import ScanState

from agents.discovery_agent import discovery_agent
from agents.detection_agent import detection_agent
from agents.validation_agent import validation_agent
from agents.context_agent import context_agent
from agents.risk_agent import risk_agent
from agents.remediation_agent import remediation_agent
from agents.reporting_agent import reporting_agent


def build_graph():
    workflow = StateGraph(ScanState)

    workflow.add_node("discovery", discovery_agent)
    workflow.add_node("detection", detection_agent)
    workflow.add_node("validation", validation_agent)
    workflow.add_node("context", context_agent)
    workflow.add_node("risk", risk_agent)
    workflow.add_node("remediation", remediation_agent)
    workflow.add_node("reporting", reporting_agent)

    workflow.set_entry_point("discovery")

    workflow.add_edge("discovery", "detection")
    workflow.add_edge("detection", "validation")
    workflow.add_edge("validation", "context")
    workflow.add_edge("context", "risk")
    workflow.add_edge("risk", "remediation")
    workflow.add_edge("remediation", "reporting")

    workflow.set_finish_point("reporting")

    return workflow.compile()
