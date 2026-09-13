const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

function resolveApiUrl(path: string): string {
  const normalizedBase = API_BASE.replace(/\/$/, '');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

async function safeFetch(url: string, options?: RequestInit) {
  const reqOptions: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
  };
  const response = await fetch(url, reqOptions);
  let data: any = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e) {
      data = { message: text };
    }
  }

  if (!response.ok) {
    const errorMsg = data?.error || data?.detail || data?.message || `HTTP ${response.status}`;
    throw new Error(errorMsg);
  }
  return data;
}

export async function getCustomers() {
  return safeFetch(resolveApiUrl('/customers'));
}

export async function getCustomer(id: number | string) {
  return safeFetch(resolveApiUrl(`/customers/${id}`));
}

export async function getProfile(id: number | string) {
  return safeFetch(resolveApiUrl(`/customers/${id}/profile`));
}

export async function getGuardian(id: number | string) {
  return safeFetch(resolveApiUrl(`/customers/${id}/guardian`));
}

export async function getRecommendation(id: number | string) {
  return safeFetch(resolveApiUrl(`/customers/${id}/recommendation`));
}

export async function getTransactions(id: number | string) {
  return safeFetch(resolveApiUrl(`/customers/${id}/transactions`));
}

export async function createTransaction(id: number | string, transaction: any) {
  return safeFetch(resolveApiUrl(`/customers/${id}/transactions`), {
    method: 'POST',
    body: JSON.stringify(transaction),
  });
}

export async function chatWithSakhi(customerId: number | string, message: string) {
  const data = await safeFetch(resolveApiUrl('/chat'), {
    method: 'POST',
    body: JSON.stringify({ customer_id: Number(customerId), message: message.trim() }),
  });
  return {
    ...data,
    reply: data.reply || data.message || '',
  };
}

// Appointments
export async function getAppointments(customerId: number | string) {
  try {
    return await safeFetch(resolveApiUrl(`/customers/${customerId}/appointments`));
  } catch {
    return [];
  }
}

export async function getAdvisorContext(customerId: number | string) {
  try {
    return await safeFetch(resolveApiUrl(`/customers/${customerId}/advisor-context`));
  } catch {
    return { should_offer: false };
  }
}

export async function getAdvisorAvailability(date: string, advisorType?: string) {
  try {
    let endpoint = `/appointments/availability?date=${encodeURIComponent(date)}`;
    if (advisorType) {
      endpoint += `&advisor_type=${encodeURIComponent(advisorType)}`;
    }
    return await safeFetch(resolveApiUrl(endpoint));
  } catch {
    return { available_slots: [] };
  }
}

export async function bookAppointment(customerId: number | string, payload: any) {
  return safeFetch(resolveApiUrl(`/customers/${customerId}/appointments`), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function cancelAppointment(appointmentId: string) {
  return safeFetch(resolveApiUrl(`/appointments/${appointmentId}`), {
    method: 'DELETE',
  });
}
