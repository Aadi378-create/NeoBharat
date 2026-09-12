/**
 * NeoBharat API Client (Phase 6B).
 *
 * Consumes existing backend REST APIs.
 * The frontend acts strictly as a presentation layer. It NEVER calculates
 * metrics, scores, classifications, or decisions.
 */

const API_BASE = '';

/**
 * Handle HTTP response and parse JSON.
 * Throws clean error on non-2xx or malformed JSON.
 */
async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errData = await response.json();
      if (errData && errData.error) {
        errorMsg = errData.error;
      }
    } catch {
      // Non-JSON error body (e.g. 404 HTML)
    }
    throw new Error(errorMsg);
  }

  try {
    return await response.json();
  } catch (err) {
    throw new Error(`Failed to parse backend response as JSON: ${err.message}`);
  }
}

/**
 * Fetch all seeded customers for the customer selector.
 */
export async function fetchCustomers() {
  const res = await fetch(`${API_BASE}/api/customers`);
  return handleResponse(res);
}

/**
 * Fetch individual customer identity.
 */
export async function fetchCustomer(customerId) {
  const res = await fetch(`${API_BASE}/api/customers/${customerId}`);
  return handleResponse(res);
}

/**
 * Fetch pre-calculated deterministic financial profile.
 */
export async function fetchProfile(customerId) {
  const res = await fetch(`${API_BASE}/api/customers/${customerId}/profile`);
  return handleResponse(res);
}

/**
 * Fetch pre-evaluated Guardian assessment.
 */
export async function fetchGuardian(customerId) {
  const res = await fetch(`${API_BASE}/api/customers/${customerId}/guardian`);
  return handleResponse(res);
}

/**
 * Fetch pre-evaluated Phase 3 decision and recommendation.
 */
export async function fetchRecommendation(customerId) {
  const res = await fetch(`${API_BASE}/api/customers/${customerId}/recommendation`);
  return handleResponse(res);
}

/**
 * Send conversational chat message to the OpenAI explanation layer.
 *
 * Strict safety rules:
 * - Reject messages over 4000 characters before sending HTTP request.
 * - Request payload contains ONLY `customer_id` and `message`.
 * - Never send client-computed financial values, scores, or decisions.
 */
export async function sendChatMessage(customerId, message) {
  if (typeof message !== 'string') {
    throw new Error('Message must be a string.');
  }

  const trimmed = message.trim();
  if (!trimmed) {
    throw new Error('Message cannot be empty.');
  }

  if (message.length > 4000) {
    throw new Error('Message exceeds the maximum allowed length of 4000 characters.');
  }

  const payload = {
    customer_id: Number(customerId),
    message: trimmed,
  };

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  return handleResponse(res);
}
