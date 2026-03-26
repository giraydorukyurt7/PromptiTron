"use client";

import Link from "next/link";
import Logo from "../logo";
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { cn } from "@/lib/utils";
import {
    Globe,
    Youtube,
    FileText,
    Search,
    MessageSquare,
    Calendar,
    Activity,
    BookOpen,
    GraduationCap,
} from "lucide-react";

const services = [
    {
        title: "Web Analizi",
        href: "/services/web-analysis",
        description: "Web sitelerini eğitim değeri açısından analiz edin",
        icon: Globe,
    },
    {
        title: "YouTube Analizi",
        href: "/services/youtube-analysis",
        description: "YouTube videolarını YKS müfredatına göre analiz edin",
        icon: Youtube,
    },
    {
        title: "Doküman Analizi",
        href: "/services/document-analysis",
        description: "PDF ve dokümanları analiz edin",
        icon: FileText,
    },
    {
        title: "İçerik Analizi",
        href: "/services/content-analysis",
        description: "Metin içeriklerini detaylı analiz edin",
        icon: FileText,
    },
    {
        title: "Arama",
        href: "/services/search",
        description: "Eğitim içeriklerinde arama yapın",
        icon: Search,
    },
    {
        title: "Sorular",
        href: "/services/questions",
        description: "İçerikten soru üretin",
        icon: MessageSquare,
    },
    {
        title: "Çalışma Planı",
        href: "/services/study-plan",
        description: "Kişiselleştirilmiş çalışma planı oluşturun",
        icon: Calendar,
    },
    {
        title: "Sistem Durumu",
        href: "/services/system-status",
        description: "Sistem durumunu kontrol edin",
        icon: Activity,
    },
];

const curriculum = [
    {
        title: "AI Sohbet",
        href: "/curriculum/ai-chat",
        description: "AI ile etkileşimli öğrenme",
        icon: MessageSquare,
    },
    {
        title: "Özet",
        href: "/curriculum/summary",
        description: "Konu özetleri oluştur",
        icon: FileText,
    },
    {
        title: "Açıklama",
        href: "/curriculum/explanation",
        description: "Detaylı konu açıklamaları",
        icon: BookOpen,
    },
    {
        title: "Sorular",
        href: "/curriculum/questions",
        description: "Pratik soruları çöz",
        icon: MessageSquare,
    },
    {
        title: "Kavram Haritası",
        href: "/curriculum/concept-map",
        description: "Görsel kavram haritaları",
        icon: Globe,
    },
    {
        title: "Sokratik Öğrenme",
        href: "/curriculum/socratic",
        description: "Soru-cevap ile öğren",
        icon: GraduationCap,
    },
];

const ListItem = ({
    className,
    title,
    children,
    icon: Icon,
    ...props
}: any) => {
    return (
        <li>
            <NavigationMenuLink asChild>
                <Link
                    className={cn(
                        "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
                        className,
                    )}
                    {...props}
                >
                    <div className="flex items-center gap-2">
                        {Icon && <Icon className="h-4 w-4" />}
                        <div className="text-sm font-medium leading-none">
                            {title}
                        </div>
                    </div>
                    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
                        {children}
                    </p>
                </Link>
            </NavigationMenuLink>
        </li>
    );
};

export default function Header() {
    return (
        <header className="border-b">
            <div className="container-x py-3">
                <div className="flex items-center justify-between w-full">
                    <div className="flex items-center justify-between w-full gap-8">
                        <Logo />

                        <NavigationMenu>
                            <NavigationMenuList>
                                <NavigationMenuItem>
                                    <NavigationMenuLink
                                        asChild
                                        className={navigationMenuTriggerStyle()}
                                    >
                                        <Link href="/">Ana Sayfa</Link>
                                    </NavigationMenuLink>
                                </NavigationMenuItem>

                                <NavigationMenuItem>
                                    <NavigationMenuTrigger>
                                        Servisler
                                    </NavigationMenuTrigger>
                                    <NavigationMenuContent>
                                        <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
                                            {services.map((service) => (
                                                <ListItem
                                                    key={service.title}
                                                    title={service.title}
                                                    href={service.href}
                                                    icon={service.icon}
                                                >
                                                    {service.description}
                                                </ListItem>
                                            ))}
                                        </ul>
                                    </NavigationMenuContent>
                                </NavigationMenuItem>

                                <NavigationMenuItem>
                                    <NavigationMenuTrigger>
                                        Müfredat
                                    </NavigationMenuTrigger>
                                    <NavigationMenuContent>
                                        <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
                                            {curriculum.map((item) => (
                                                <ListItem
                                                    key={item.title}
                                                    title={item.title}
                                                    href={item.href}
                                                    icon={item.icon}
                                                >
                                                    {item.description}
                                                </ListItem>
                                            ))}
                                        </ul>
                                    </NavigationMenuContent>
                                </NavigationMenuItem>

                                <NavigationMenuItem>
                                    <NavigationMenuTrigger>
                                        Sınav Hazırlık
                                    </NavigationMenuTrigger>
                                    <NavigationMenuContent>
                                        <ul className="grid gap-3 p-6 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]">
                                            <li className="row-span-3">
                                                <NavigationMenuLink asChild>
                                                    <Link
                                                        className="flex h-full w-full select-none flex-col justify-end rounded-md bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md"
                                                        href="/ai-chat"
                                                    >
                                                        <GraduationCap className="h-6 w-6" />
                                                        <div className="mb-2 mt-4 text-lg font-medium">
                                                            AI Asistan
                                                        </div>
                                                        <p className="text-sm leading-tight text-muted-foreground">
                                                            YKS ve LGS
                                                            sınavlarına özel AI
                                                            destekli öğrenme
                                                            asistanı
                                                        </p>
                                                    </Link>
                                                </NavigationMenuLink>
                                            </li>
                                            <ListItem
                                                href="/yks"
                                                title="YKS Hazırlık"
                                            >
                                                Üniversite sınavına hazırlık
                                                materyalleri
                                            </ListItem>
                                            <ListItem
                                                href="/lgs"
                                                title="LGS Hazırlık"
                                            >
                                                Liseye geçiş sınavı hazırlık
                                                içerikleri
                                            </ListItem>
                                            <ListItem
                                                href="/services"
                                                title="Tüm Servisler"
                                            >
                                                Tüm eğitim araçlarını keşfedin
                                            </ListItem>
                                        </ul>
                                    </NavigationMenuContent>
                                </NavigationMenuItem>

                                <NavigationMenuItem>
                                    <NavigationMenuLink
                                        asChild
                                        className={navigationMenuTriggerStyle()}
                                    >
                                        <Link href="/ai-chat">AI Sohbet</Link>
                                    </NavigationMenuLink>
                                </NavigationMenuItem>
                            </NavigationMenuList>
                        </NavigationMenu>
                    </div>
                </div>
            </div>
        </header>
    );
}
