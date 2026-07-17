import type { ChatResponse } from "../types";

export function formatAssistantReply(result: ChatResponse): string {
  return result.response.message.trim();
}

export function extractReplyMeta(result: ChatResponse) {
  const citation = result.response.citations[0];
  return {
    agent: result.response.agent,
    routeReason: result.route.reason,
    citation,
    workOrderId: result.response.work_order_id,
    requiresApproval: result.response.requires_approval,
    flags: result.compliance.flags,
  };
}
