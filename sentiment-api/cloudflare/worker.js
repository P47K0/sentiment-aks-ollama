export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Read the active backend from KV
    const backend = await env.DEMO_BACKEND.get("backend_url");

    if (backend) {
      // === DEMO ACTIVE: Proxy traffic to your AKS Load Balancer ===
      try {
        const targetUrl = backend + url.pathname + url.search;

        const response = await fetch(targetUrl, {
          method: request.method,
          headers: {
            ...Object.fromEntries(request.headers),
            'Host': url.hostname,        // Keep original domain
          },
          body: request.body,
        });

        return response;
      } catch (err) {
        return new Response("Demo backend is temporarily unavailable", { 
          status: 502 
        });
      }
    } else {      
      const saleHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>demourlisd.one — Domain for Sale</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; text-align: center; padding: 100px 20px; background: #f9fafb; color: #1f2937; line-height: 1.6; }
    h1 { font-size: 3rem; margin-bottom: 16px; color: #111827; }
    p { font-size: 1.25rem; max-width: 620px; margin: 0 auto 30px; }
    .highlight { color: #2563eb; font-weight: 600; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
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