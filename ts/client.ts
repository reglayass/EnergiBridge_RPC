import { createTRPCProxyClient, httpBatchLink } from "@trpc/client";
import type { AppRouter } from "./server";

// Create a tRPC client
const client = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: "http://localhost:8080/trpc",
    }),
  ],
});

async function main() {
  try {
    console.log("Calling add(2, 3)...");

    const result = await client.add.query({ a: 2, b: 3 });
    
    console.log(`add(2, 3) = ${result}`);
  } catch (error) {
    console.error("RPC call failed:", error);
  }
}

main();
