"use client";

import { SidebarTrigger, useSidebar } from "@/components/ui/sidebar";
import { cn } from "@/lib/utils";
import { CpuIcon } from "lucide-react";

export function WorkspaceHeader({ className }: { className?: string }) {
  const { state } = useSidebar();
  return (
    <div
      className={cn(
        "group/workspace-header flex h-12 flex-col justify-center",
        className,
      )}
    >
      {state === "collapsed" ? (
        <div className="group-has-data-[collapsible=icon]/sidebar-wrapper:-translate-y flex w-full cursor-pointer items-center justify-center">
          <div className="text-primary block pt-1 group-hover/workspace-header:hidden">
            <CpuIcon className="w-5 h-5" />
          </div>
          <SidebarTrigger className="hidden pl-2 group-hover/workspace-header:block" />
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2">
          <div className="text-primary ml-2 cursor-default flex items-center gap-2">
            <CpuIcon className="w-5 h-5" />
            <span className="font-semibold">PLC 代码生成</span>
          </div>
          <SidebarTrigger />
        </div>
      )}
    </div>
  );
}
