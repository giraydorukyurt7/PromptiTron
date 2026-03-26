"use client";

import Link from "next/link";
import { usePathname } from 'next/navigation';
import { MessageCircle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export default function PromptiTron() {
    const pathName = usePathname();

    if (pathName === "/ai-chat") return null;

    return (
        <Link
            href="/ai-chat"
            className={cn(
                "fixed right-6 bottom-6 z-50",
                "group flex items-center gap-3",
                "bg-gradient-to-r from-blue-600 to-purple-600",
                "text-white font-medium",
                "px-5 py-4 rounded-full",
                "shadow-2xl shadow-blue-500/25",
                "hover:shadow-2xl hover:shadow-purple-500/30",
                "hover:scale-105 active:scale-95",
                "transition-all duration-300 ease-out",
                "hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-500",
                "before:absolute before:inset-0",
                "before:rounded-full",
                "before:bg-gradient-to-r before:from-blue-400 before:to-purple-400",
                "before:opacity-0 before:transition-opacity before:duration-300",
                "hover:before:opacity-20",
                "animate-pulse-slow"
            )}
        >
            <div className="relative flex items-center gap-2">
                {/* Animated sparkle effect */}
                <Sparkles className="absolute -top-1 -right-1 w-3 h-3 text-yellow-300 animate-sparkle" />
                
                {/* Main icon with subtle animation */}
                <div className="relative">
                    <MessageCircle className="w-6 h-6 animate-float" />
                    <span className="absolute -top-1 -right-1 flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
                    </span>
                </div>
                
                {/* Text */}
                <span className="text-sm font-semibold tracking-wide">
                    AI Asistan
                </span>
            </div>
            
            {/* Hover tooltip */}
            <div className={cn(
                "absolute right-full mr-3 top-1/2 -translate-y-1/2",
                "bg-gray-900 text-white text-xs",
                "px-3 py-2 rounded-lg",
                "opacity-0 group-hover:opacity-100",
                "transition-opacity duration-200",
                "pointer-events-none",
                "whitespace-nowrap",
                "before:content-['']",
                "before:absolute before:-right-2 before:top-1/2 before:-translate-y-1/2",
                "before:border-8 before:border-transparent before:border-l-gray-900"
            )}>
                YKS ve LGS için AI destekli öğrenme asistanı
            </div>
        </Link>
    );
}