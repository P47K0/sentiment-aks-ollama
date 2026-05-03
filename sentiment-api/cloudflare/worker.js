export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    const backend = await env.DEMO_BACKEND.get("backend_url");

    // === DEMO ACTIVE: Forward to AKS (root domain) ===
    if (url.hostname === "demourlisd.one" || url.hostname === "azure.demourlisd.one") {      
      if (backend) {        
        try {
          const targetUrl = backend + url.pathname + url.search;

          const response = await fetch(targetUrl, {
            method: request.method,
            headers: request.headers,
            body: request.body,
          });

          return response;
        } catch (err) {
          return new Response("Demo backend is temporarily unavailable", { status: 502 });
        }
      }
    } else {
      const demoOverFavicon = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.55a11 11 0 0 1 14.08 0'/%3E%3Cpath d='M1.42 9a16 16 0 0 1 21.16 0'/%3E%3Cpath d='M8.53 16.11a6 6 0 0 1 6.95 0'/%3E%3Cline x1='2' y1='2' x2='22' y2='22'/%3E%3C/svg%3E`;
      const rocketFavicon = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' fill='black'/%3E%3Cpath fill='white' d='M8 8c.828 0 1.5-.895 1.5-2S8.828 4 8 4s-1.5.895-1.5 2S7.172 8 8 8'/%3E%3Cpath fill='white' d='M11.953 8.81c-.195-3.388-.968-5.507-1.777-6.819C9.707 1.233 9.23.751 8.857.454a3.5 3.5 0 0 0-.463-.315A2 2 0 0 0 8.25.064.55.55 0 0 0 8 0a.55.55 0 0 0-.266.073 2 2 0 0 0-.142.08 4 4 0 0 0-.459.33c-.37.308-.844.803-1.31 1.57-.805 1.322-1.577 3.433-1.774 6.756l-1.497 1.826-.004.005A2.5 2.5 0 0 0 2 12.202V15.5a.5.5 0 0 0 .9.3l1.125-1.5c.166-.222.42-.4.752-.57.214-.108.414-.192.625-.281l.198-.084c.7.428 1.55.635 2.4.635s1.7-.207 2.4-.635q.1.044.196.083c.213.09.413.174.627.282.332.17.586.348.752.57l1.125 1.5a.5.5 0 0 0 .9-.3v-3.298a2.5 2.5 0 0 0-.548-1.562zM12 10.445v.055c0 .866-.284 1.585-.75 2.14.146.064.292.13.425.199.39.197.8.46 1.1.86L13 14v-1.798a1.5 1.5 0 0 0-.327-.935zM4.75 12.64C4.284 12.085 4 11.366 4 10.5v-.054l-.673.82a1.5 1.5 0 0 0-.327.936V14l.225-.3c.3-.4.71-.664 1.1-.861.133-.068.279-.135.425-.199M8.009 1.073q.096.06.226.163c.284.226.683.621 1.09 1.28C10.137 3.836 11 6.237 11 10.5c0 .858-.374 1.48-.943 1.893C9.517 12.786 8.781 13 8 13s-1.517-.214-2.057-.607C5.373 11.979 5 11.358 5 10.5c0-4.182.86-6.586 1.677-7.928.409-.67.81-1.082 1.096-1.32q.136-.113.236-.18Z'/%3E%3Cpath fill='white' d='M9.479 14.361c-.48.093-.98.139-1.479.139s-.999-.046-1.479-.139L7.6 15.8a.5.5 0 0 0 .8 0z'/%3E%3C/svg%3E`;
      const favicon = backend === "" ? demoOverFavicon : rocketFavicon;
      const bgColor = backend === "" ? "white" : "darkgray"
      const saleHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>demourlisd.one — Domain for Sale</title>
  <link rel="icon" href="${favicon}" type="image/svg+xml">
  <style>
    body { 
      font-family: system-ui, -apple-system, sans-serif; 
      text-align: center; 
      padding: 120px 20px; 
      background: ${bgColor}; 
      color: #1e2937; 
      line-height: 1.6; 
    }
    h1 { font-size: 3.2rem; margin-bottom: 16px; color: #111827; }
    p { font-size: 1.3rem; max-width: 660px; margin: 0 auto 32px; }
    .highlight { color: #2563eb; font-weight: 600; }
  </style>
</head>
<body>
  <h1>demourlisd.one | demo url is done</h1>
  <p>This professional domain is currently <span class="highlight">available for sale</span>.</p>
  <p>Built as an AZ-400 practice project: ephemeral Azure AKS demos with automatic $0 idle state using Cloudflare Workers + KV.</p>
  <p>Interested? Feel free to <a href="https://www.linkedin.com/in/patrickkoorevaar/" target="_blank">get in touch</a>.</p>
</body>
</html>`;

      return new Response(saleHtml, {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }
  }
};