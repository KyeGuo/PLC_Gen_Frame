import { ChevronUpIcon, ListTodoIcon } from "lucide-react";
import { useEffect, useState } from "react";

import type { Todo } from "@/core/todos";
import { cn } from "@/lib/utils";

import {
  QueueItem,
  QueueItemContent,
  QueueItemIndicator,
  QueueList,
} from "../ai-elements/queue";

export function TodoList({
  className,
  todos,
  collapsed: controlledCollapsed,
  hidden = false,
  onToggle,
  onHeightChange,
}: {
  className?: string;
  todos: Todo[];
  collapsed?: boolean;
  hidden?: boolean;
  onToggle?: () => void;
  onHeightChange?: (height: number) => void;
}) {
  const [internalCollapsed, setInternalCollapsed] = useState(true);
  const isControlled = controlledCollapsed !== undefined;
  const collapsed = isControlled ? controlledCollapsed : internalCollapsed;

  const handleToggle = () => {
    if (isControlled) {
      onToggle?.();
    } else {
      setInternalCollapsed((prev) => !prev);
    }
  };

  // 使用 useEffect 在状态更新后通知父组件高度变化
  useEffect(() => {
    if (!isControlled && onHeightChange) {
      const height = collapsed ? 32 : 144; // collapsed: 32px, expanded: 144px
      onHeightChange(height);
    }
  }, [collapsed, isControlled, onHeightChange]);

  return (
    <div
      className={cn(
        "flex h-fit w-full origin-bottom flex-col overflow-hidden rounded-t-xl border border-b-0 bg-white/95 backdrop-blur-md shadow-lg shadow-black/5",
        hidden ? "pointer-events-none translate-y-8 opacity-0" : "",
        className,
      )}
      style={{
        // 添加过渡效果，避免闪烁
        transition: hidden ? "all 0.3s ease-out" : undefined,
      }}
    >
      <header
        className={cn(
          "bg-accent/80 flex min-h-8 shrink-0 cursor-pointer items-center justify-between px-4 text-sm",
          "border-b border-border/50",
        )}
        onClick={handleToggle}
      >
        <div className="text-muted-foreground">
          <div className="flex items-center justify-center gap-2">
            <ListTodoIcon className="size-4" />
            <div className="font-medium">To-dos</div>
            {todos.length > 0 && (
              <span className="rounded-full bg-muted px-1.5 py-0.5 text-xs">
                {todos.length}
              </span>
            )}
          </div>
        </div>
        <div>
          <ChevronUpIcon
            className={cn(
              "text-muted-foreground size-4 transition-transform duration-200",
              collapsed ? "" : "rotate-180",
            )}
          />
        </div>
      </header>
      <main
        className={cn(
          "bg-background/50 flex grow px-3 py-2",
          collapsed ? "h-0 overflow-hidden" : "h-32 overflow-y-auto",
        )}
        style={{
          transition: "height 0.3s ease-out",
        }}
      >
        <QueueList className="bg-transparent mt-0 w-full">
          {todos.map((todo, i) => (
            <QueueItem key={i + (todo.content ?? "")} className="py-1">
              <div className="flex items-center gap-2">
                <QueueItemIndicator
                  className={cn(
                    "size-4",
                    todo.status === "in_progress" ? "bg-primary/70" : "",
                  )}
                  completed={todo.status === "completed"}
                />
                <QueueItemContent
                  className={cn(
                    "text-sm",
                    todo.status === "in_progress" ? "text-primary" : "",
                    todo.status === "completed" ? "text-muted-foreground line-through" : "",
                  )}
                  completed={todo.status === "completed"}
                >
                  {todo.content}
                </QueueItemContent>
              </div>
            </QueueItem>
          ))}
        </QueueList>
      </main>
    </div>
  );
}
