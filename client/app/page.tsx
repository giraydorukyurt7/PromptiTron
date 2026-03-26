import { Button } from "@/components/ui/button";
import { categories } from "@/lib/constants/lessons";
import Link from "next/link";
import Image from "next/image";

export default function Home() {
    return (
        <>
            <section className="container-x flex-center flex-col min-h-[80dvh]">
                <h1 className="text-4xl font-semibold text-center capitalize mb-2.5 mt-4">
                    PromptiTron AI Eğitim Sistemi
                </h1>

                <p className="text-gray-600 text-center max-w-2xl">
                    YKS&apos;ye hazırlanırken size yardımcı olacak yapay zeka
                    destekli eğitim araçları
                </p>

                <div className="relative">
                    <Image
                        src="/logo.png"
                        alt="PromptitTron Logo"
                        width={500}
                        height={500}
                        className="object-contain"
                        priority
                    />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl mb-8">
                    {/* Categories */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h2 className="text-xl font-semibold mb-4">
                            Eğitim Seviyeleri
                        </h2>
                        <div className="space-y-3">
                            {categories.map((category) => (
                                <Button
                                    key={category.id}
                                    asChild={category.isActive}
                                    variant={
                                        category.isActive
                                            ? "default"
                                            : "outline"
                                    }
                                    disabled={!category.isActive}
                                    className={`w-full justify-start ${
                                        !category.isActive
                                            ? "opacity-50 cursor-not-allowed"
                                            : ""
                                    }`}
                                >
                                    {category.isActive ? (
                                        <Link href={category.href}>
                                            {category.title}
                                        </Link>
                                    ) : (
                                        <span>{category.title}</span>
                                    )}
                                </Button>
                            ))}
                        </div>
                    </div>

                    {/* Services */}
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <h2 className="text-xl font-semibold mb-4">
                            AI Servisleri
                        </h2>
                        <div className="space-y-3">
                            <Button asChild className="w-full justify-start">
                                <Link href="/services">Tüm AI Servisler</Link>
                            </Button>
                            <Button
                                asChild
                                variant="outline"
                                className="w-full justify-start"
                            >
                                <Link href="/ai-chat">AI Asistan</Link>
                            </Button>
                            <Button
                                asChild
                                variant="outline"
                                className="w-full justify-start"
                            >
                                <Link href="/services/questions">
                                    Soru Oluştur
                                </Link>
                            </Button>
                            <Button
                                asChild
                                variant="outline"
                                className="w-full justify-start"
                            >
                                <Link href="/services/study-plan">
                                    Çalışma Planı
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}
