import Link from "next/link";
import Image from "next/image";

interface LogoProps {
    size?: "sm" | "md" | "lg" | "xl";
    showText?: boolean;
    className?: string;
}

const sizeMap = {
    sm: { width: 32, height: 32, textSize: "text-lg" },
    md: { width: 48, height: 48, textSize: "text-xl" },
    lg: { width: 64, height: 64, textSize: "text-2xl" },
    xl: { width: 96, height: 96, textSize: "text-4xl" }
};

export default function Logo({ size = "md", showImg= false, showText = true, className = "" }: LogoProps) {
    const { width, height, textSize } = sizeMap[size];
    
    return (
        <Link href="/" className={`flex items-center gap-3 hover:opacity-80 transition-opacity ${className}`}>
            {showImg && (
                <div className="relative">
                <Image
                    src="/logo.png"
                    alt="PromptitTron Logo"
                    width={width}
                    height={height}
                    className="object-contain"
                    priority
                />
            </div>)}
            {showText && (
                <span className={`font-bold text-primary ${textSize}`}>
                    Prompti<span className="text-secondary">Tron</span>
                </span>
            )}
        </Link>
    );
}