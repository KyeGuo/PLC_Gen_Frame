"use client";

import { Button } from "@/components/ui/button";
import { ArrowRightIcon, ZapIcon, CpuIcon, CheckCircleIcon, SettingsIcon } from "lucide-react";
import Link from "next/link";

export default function PLCLandingPage() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-gray-950 to-gray-900">
      {/* Header */}
      <header className="w-full border-b border-gray-800 bg-gray-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CpuIcon className="w-8 h-8 text-blue-500" />
            <h1 className="text-xl font-bold text-white">PLC 代码生成器</h1>
          </div>
          <Link href="/workspace/agents">
            <Button variant="default" className="bg-blue-600 hover:bg-blue-700">
              开始使用
              <ArrowRightIcon className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 bg-blue-950/50 rounded-full border border-blue-800">
            <ZapIcon className="w-4 h-4 text-blue-400" />
            <span className="text-blue-300 text-sm">基于 DeerFlow 的智能体协作</span>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            自动生成高质量 PLC 代码
          </h2>

          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            利用 AI 智能体协作，快速生成符合 TwinCAT 规范的 PLC 代码，支持自动验证和优化
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link href="/workspace/agents">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-6">
                开始生成代码
                <ArrowRightIcon className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-800">
              <div className="w-12 h-12 bg-blue-900/50 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <CpuIcon className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">智能体协作</h3>
              <p className="text-gray-400 text-sm">设计、编码、验证、优化全流程自动化</p>
            </div>

            <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-800">
              <div className="w-12 h-12 bg-green-900/50 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <CheckCircleIcon className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">自动验证</h3>
              <p className="text-gray-400 text-sm">基于 TwinCAT 规范的代码质量检查</p>
            </div>

            <div className="p-6 bg-gray-900/50 rounded-xl border border-gray-800">
              <div className="w-12 h-12 bg-purple-900/50 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <SettingsIcon className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">代码优化</h3>
              <p className="text-gray-400 text-sm">智能修复和优化，确保代码质量</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 mt-16">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          <p>PLC 代码生成器 - 基于 DeerFlow 框架</p>
        </div>
      </footer>
    </div>
  );
}
