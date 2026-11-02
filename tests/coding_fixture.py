"""A deliberately small non-authentication application for zero-fee loop verification."""

import json
import base64

from coding_agent.trace import sha

REFERENCE_IMAGE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="
)
SETUP = {
    "APP_CONTRACT.md": "# Notes\nREQ-1: GET /api/items is read-only; POST {title} saves one note, blank title rejects without writes. Homepage lists notes and survives reload.\n",
    "backend/src/db/tables/Item.sql": "CREATE TABLE IF NOT EXISTS Item(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL);\n",
    "backend/tests/contract.test.ts": """import {test} from "node:test";
import assert from "node:assert/strict";
import {appFixture} from "./support/http.js";
test("REQ-1 persists one note and lists it read-only",async t=>{
 const {send,database}=await appFixture(t);
 const created=await send("POST","/api/items",{title:"fixture note"});
 assert.equal(created.status,201);
 assert.equal(database.prepare("SELECT COUNT(*) n FROM Item").get() && (database.prepare("SELECT COUNT(*) n FROM Item").get() as any).n,1);
 const before=database.prepare("SELECT * FROM Item").all();
 const listed=await send("GET","/api/items");assert.equal(listed.status,200);
 assert.equal(listed.body.length,1);assert.equal(listed.body[0].title,"fixture note");
 assert.deepEqual(database.prepare("SELECT * FROM Item").all(),before);
});
test("REQ-1 blank title is rejected without writes",async t=>{
 const {send,database}=await appFixture(t);const r=await send("POST","/api/items",{title:""});
 assert.equal(r.status,400);assert.deepEqual(database.prepare("SELECT * FROM Item").all(),[]);
});\n""",
    "frontend/tests/ui/presence.spec.ts": """import {test,expect} from "../e2e/support/context.js";
test("REQ-1 exact note controls",async({page})=>{
 await page.goto("/");await expect(page.getByRole("heading",{name:"Notes",exact:true})).toBeVisible();
 await expect(page.getByRole("textbox",{name:"Title",exact:true})).toBeVisible();
 await expect(page.getByRole("button",{name:"Save",exact:true})).toBeVisible();
});\n""",
    "frontend/tests/e2e/workflows.spec.ts": """import {test,expect} from "./support/context.js";
test("REQ-1 save and reload persistence",async({page,database})=>{
 await page.goto("/");const title=page.getByRole("textbox",{name:"Title",exact:true});
 await expect(title).toBeVisible();await title.fill("persistent fixture");
 const save=page.getByRole("button",{name:"Save",exact:true});await expect(save).toBeVisible();await save.click();
 await expect(page.getByRole("listitem")).toHaveText("persistent fixture");
 expect((database.prepare("SELECT * FROM Item").all() as any[])[0].title).toBe("persistent fixture");
 await page.reload();await expect(page.getByRole("listitem")).toHaveText("persistent fixture");
});\n""",
}

INITIALIZER = """import type Database from "better-sqlite3";
import {readFileSync} from "node:fs";
export const tableFiles=["Item.sql"];
export function initializeDatabase(connection:Database.Database){
 connection.pragma("foreign_keys=ON");
 for(const name of tableFiles)connection.exec(readFileSync(new URL(`./tables/${name}`,import.meta.url),"utf8"));
}\n"""

BACKEND = """import type {Express} from "express";
import type Database from "better-sqlite3";
export function registerApis(app:Express,db:Database.Database){
 app.get("/api/items",(_req,res)=>res.json(db.prepare("SELECT * FROM Item ORDER BY id").all()));
 app.post("/api/items",(req,res)=>{
  const title=req.body?.title;
  if(typeof title!=="string"||!title.trim()){res.status(400).json({error:"Title required"});return;}
  const result=db.prepare("INSERT INTO Item(title) VALUES(?)").run(title);
  res.status(201).json({id:Number(result.lastInsertRowid),title});
 });
}\n"""

FRONTEND = """import {useEffect,useState} from "react";
export function App(){
 const [items,setItems]=useState<{id:number,title:string}[]>([]),[title,setTitle]=useState("");
 async function refresh(){const r=await fetch("/api/items");if(r.ok)setItems(await r.json());}
 useEffect(()=>{void refresh()},[]);
 return <main><h1>Notes</h1><form onSubmit={async e=>{e.preventDefault();await fetch("/api/items",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({title})});await refresh();setTitle("")}}>
 <label htmlFor="title">Title</label><input id="title" value={title} onChange={e=>setTitle(e.target.value)}/><button type="submit">Save</button></form>
 <ul>{items.map(item=><li key={item.id}>{item.title}</li>)}</ul></main>;
}\n"""


def replacement(output, path, content):
    target = output / path
    if not target.exists():
        return {"path": path, "content": content}
    return {
        "path": path,
        "expected_sha256": sha(target),
        "old_text": target.read_text(),
        "new_text": content,
    }


class FixtureModel:
    """Scripted tools make a genuine cross-layer error and then repair it."""

    def __init__(self, config, trace):
        self.output, self.trace, self.index = config.output, trace, 0
        self.inputs = getattr(config, "inputs", self.output.parent / "input")

    def next_action(self):
        self.index += 1
        if self.index == 1:
            return {
                "action": "edit",
                "edits": [replacement(self.output, p, c) for p, c in SETUP.items()]
                + [
                    replacement(
                        self.output, "backend/src/db/initialize.ts", INITIALIZER
                    )
                ],
            }
        if self.index == 2:
            return {"action": "finish"}
        if self.index == 3:
            return {
                "action": "edit",
                "edits": [
                    replacement(self.output, "backend/src/api/register.ts", BACKEND),
                    replacement(
                        self.output,
                        "frontend/src/App.tsx",
                        FRONTEND.replace("<h1>Notes</h1>", "<h1>Wrong title</h1>"),
                    ),
                ]
                + (
                    [
                        {
                            "path": "frontend/public/assets/reference.png",
                            "copy_from": "input/reference.png",
                        }
                    ]
                    if (self.inputs / "reference.png").is_file()
                    else []
                ),
            }
        if self.index == 4:
            return {"action": "check", "name": "all"}
        if self.index == 5:
            return {
                "action": "edit",
                "edits": [replacement(self.output, "frontend/src/App.tsx", FRONTEND)],
            }
        return {"action": "finish"}

    def generate(self, messages, remaining):
        action = self.next_action()
        call = f"fixture-{self.index}"
        self.trace.emit("model.request", call_id=call)
        self.trace.response(
            call,
            {
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 3,
                    "total_tokens": 13,
                }
            },
        )
        return action, json.dumps(action)
