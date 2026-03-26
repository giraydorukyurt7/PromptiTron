"use client";

import { API_MODULES } from "@/lib/constants/lessons";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function ServicesPage() {
  return (
    <div className="container-x py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          PromptiTron API Servisleri
        </h1>
        <p className="text-gray-600">
          YKS eğitimi için geliştirilen AI destekli servisleri keşfedin
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {API_MODULES.map((module) => {
          const IconComponent = module.icon;
          
          return (
            <div
              key={module.id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className={`${module.color} p-3 rounded-lg text-white flex-shrink-0`}>
                  <IconComponent className="w-6 h-6" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {module.name}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4">
                    {module.description}
                  </p>
                  
                  <Button asChild size="sm" className="w-full">
                    <Link href={module.href}>
                      Kullan
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}