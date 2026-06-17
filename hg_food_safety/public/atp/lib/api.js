const ctx = window.FS_CONTEXT || {};

export async function call(method, args = {}) {
  const res = await fetch(ctx.baseUrl + method, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Frappe-CSRF-Token": ctx.csrf || "",
    },
    body: JSON.stringify(args),
  });
  if (!res.ok) {
    let msg = "Loi " + res.status;
    try { const e = await res.json(); msg = (e._server_messages || e.message || msg); } catch (e) {}
    throw new Error(msg);
  }
  const data = await res.json();
  return data.message;
}
