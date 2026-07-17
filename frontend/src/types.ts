export interface Unit {
  id: string;
  property_name: string;
  label: string;
}

export interface Citation {
  lease_id: string;
  section: string;
  title: string;
  excerpt: string;
  score: number;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  unit_id?: string | null;
}

export interface RouteDecision {
  agent: string;
  confidence: number;
  reason: string;
}

export interface ComplianceResult {
  requires_approval: boolean;
  is_urgent: boolean;
  flags: string[];
  sanitized_response: string | null;
}

export interface AgentResponse {
  agent: string;
  message: string;
  citations: Citation[];
  work_order_id: string | null;
  requires_approval: boolean;
  approval_id: string | null;
  metadata: Record<string, unknown>;
}

export interface ChatResponse {
  session_id: string;
  route: RouteDecision;
  response: AgentResponse;
  compliance: ComplianceResult;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  meta?: {
    agent?: string;
    routeReason?: string;
    citation?: Citation;
    workOrderId?: string | null;
    requiresApproval?: boolean;
    flags?: string[];
  };
}
