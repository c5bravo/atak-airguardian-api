import { Elysia } from "elysia";
import { cors } from "@elysiajs/cors";
import { radarRouter } from "./radar";

const app = new Elysia().use(cors()).use(radarRouter).listen(8000);
