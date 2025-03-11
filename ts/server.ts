import express from "express";
import cors from "cors";
import { initTRPC } from "@trpc/server";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { z } from "zod";

const t = initTRPC.create();

// Define router with RPC functions
const appRouter = t.router({
  add: t.procedure
    .input(z.object({ a: z.number(), b: z.number() }))
    .query(({ input }) => input.a + input.b),

  sub: t.procedure
    .input(z.object({ a: z.number(), b: z.number() }))
    .query(({ input }) => input.a - input.b),

  mul: t.procedure
    .input(z.object({ a: z.number(), b: z.number() }))
    .query(({ input }) => input.a * input.b),

  div: t.procedure
    .input(z.object({ a: z.number(), b: z.number() }))
    .query(({ input }) => {
      if (input.b === 0) {
        throw new Error("Division by zero is not allowed.");
      }
      return input.a / input.b;
    }),
});

const app = express();
app.use(cors());
app.use(express.json());

app.use("/trpc", createExpressMiddleware({ router: appRouter }));

// Start server
const PORT = 8080;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});

// Export types for client
export type AppRouter = typeof appRouter;
