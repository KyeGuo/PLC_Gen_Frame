"use client";

import { BotIcon } from "lucide-react";

import { useAgents } from "@/core/agents";

import { AgentCard } from "./agent-card";

export function AgentGallery() {
  const { agents, isLoading } = useAgents();

  // 排序智能体：plc-coordinator 放在第一位，其他按字母序排列
  const sortedAgents = [...agents].sort((a, b) => {
    if (a.name === "plc-coordinator") return -1;
    if (b.name === "plc-coordinator") return 1;
    return a.name.localeCompare(b.name);
  });

  return (
    <div className="flex size-full flex-col">
      {/* Page header */}
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold">PLC 智能体</h1>
          <p className="text-muted-foreground mt-0.5 text-sm">
            选择相应的智能体开始任务
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="text-muted-foreground flex h-40 items-center justify-center text-sm">
            加载中...
          </div>
        ) : sortedAgents.length === 0 ? (
          <div className="flex h-64 flex-col items-center justify-center gap-3 text-center">
            <div className="bg-muted flex h-14 w-14 items-center justify-center rounded-full">
              <BotIcon className="text-muted-foreground h-7 w-7" />
            </div>
            <div>
              <p className="font-medium">暂无智能体</p>
              <p className="text-muted-foreground mt-1 text-sm">
                请确保后端服务已正确配置
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {sortedAgents.map((agent) => (
              <AgentCard key={agent.name} agent={agent} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
