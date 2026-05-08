"use client";

import { BotIcon, MessageSquareIcon } from "lucide-react";
import { useRouter } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Agent } from "@/core/agents";

interface AgentCardProps {
  agent: Agent;
}

const agentRoles: Record<string, { title: string; description: string }> = {
  "plc-coordinator": {
    title: "总协调智能体",
    description: "负责协调整个 PLC 代码生成流程，接收需求并调用其他智能体完成任务"
  },
  "plc-designer": {
    title: "方案设计智能体",
    description: "分析需求并设计 PLC 架构、功能块和数据结构"
  },
  "plc-coder": {
    title: "代码编写智能体",
    description: "根据设计方案生成符合 TwinCAT 规范的 PLC 代码文件"
  },
  "plc-validator": {
    title: "代码验证智能体",
    description: "使用 TwinCAT MCP 工具验证代码的质量和合规性"
  },
  "plc-optimizer": {
    title: "代码优化智能体",
    description: "修复和优化 PLC 代码，提高代码质量"
  }
};

export function AgentCard({ agent }: AgentCardProps) {
  const router = useRouter();
  const isCoordinator = agent.name === "plc-coordinator";
  const role = agentRoles[agent.name] || { title: "智能体", description: agent.description || "" };

  function handleChat() {
    router.push(`/workspace/agents/${agent.name}/chats/new`);
  }

  return (
    <Card className={`group flex flex-col transition-shadow hover:shadow-md ${isCoordinator ? 'border-blue-500/50 bg-blue-950/10' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className={`bg-primary/10 text-primary flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${isCoordinator ? 'bg-blue-500/20 text-blue-400' : ''}`}>
              <BotIcon className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <CardTitle className="truncate text-base">
                {role.title}
              </CardTitle>
              <Badge variant="secondary" className="mt-0.5 text-xs">
                {agent.name}
              </Badge>
            </div>
          </div>
        </div>
        <CardDescription className="mt-2 text-sm">
          {role.description}
        </CardDescription>
      </CardHeader>

      {agent.tool_groups && agent.tool_groups.length > 0 && (
        <CardContent className="pt-0 pb-3">
          <div className="flex flex-wrap gap-1">
            {agent.tool_groups.map((group) => (
              <Badge key={group} variant="outline" className="text-xs">
                {group}
              </Badge>
            ))}
          </div>
        </CardContent>
      )}

      {isCoordinator && (
        <CardFooter className="mt-auto pt-3">
          <Button size="sm" className="flex-1 bg-blue-600 hover:bg-blue-700" onClick={handleChat}>
            <MessageSquareIcon className="mr-1.5 h-3.5 w-3.5" />
            开始对话
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
