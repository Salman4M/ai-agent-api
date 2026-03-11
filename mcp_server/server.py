from fastmcp import FastMCP
from fastmcp.experimental.transforms.code_mode import CodeMode,MontySandboxProvider


from agent_v2.tools import web_search,calculator,code_executor

#monty is still under development, so can't implement codemode due to api conflicts
# sandbox = MontySandboxProvider(
#     limits={"max_duration_secs":10, "max_memory":50_000_000}
# )

# mcp = FastMCP("research-server",transforms=[CodeMode(sandbox_provider=sandbox)])
mcp = FastMCP("research-server")

mcp.tool(web_search)
mcp.tool(calculator)
mcp.tool(code_executor)

if __name__ == "__main__":
    mcp.run()