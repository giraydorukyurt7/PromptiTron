"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import Logo from "@/components/logo";
import { Home, Search, ArrowLeft, BookOpen, Settings } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <div className="text-4xl font-bold">
            <Logo />
          </div>
        </div>

        {/* 404 Illustration */}
        <div className="relative">
          <div className="text-9xl font-extrabold text-gray-200 select-none">
            404
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-white rounded-full p-8 shadow-lg border border-gray-200">
              <Search className="w-16 h-16 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Error Message */}
        <div className="space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Sayfa Bulunamadı
          </h1>
          <p className="text-lg text-gray-600 max-w-md mx-auto">
            Aradığınız sayfa kaldırılmış, adı değiştirilmiş veya geçici olarak kullanılamıyor olabilir.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button asChild size="lg" className="min-w-[160px]">
            <Link href="/" className="flex items-center gap-2">
              <Home className="w-4 h-4" />
              Ana Sayfa
            </Link>
          </Button>
          
          <Button asChild variant="outline" size="lg" className="min-w-[160px]">
            <Link href="/services" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Servisler
            </Link>
          </Button>
        </div>

        {/* Quick Links */}
        <div className="border-t border-gray-200 pt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Popüler Sayfalar
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Link 
              href="/yks" 
              className="flex items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors text-sm"
            >
              <BookOpen className="w-4 h-4 text-blue-600" />
              <span className="text-gray-700">YKS Kazanımları</span>
            </Link>
            
            <Link 
              href="/services/questions" 
              className="flex items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors text-sm"
            >
              <div className="w-4 h-4 text-green-600">❓</div>
              <span className="text-gray-700">Soru Oluştur</span>
            </Link>
            
            <Link 
              href="/services/content-analysis" 
              className="flex items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors text-sm"
            >
              <div className="w-4 h-4 text-purple-600">📊</div>
              <span className="text-gray-700">İçerik Analizi</span>
            </Link>
            
            <Link 
              href="/services/youtube-analysis" 
              className="flex items-center gap-2 p-3 bg-white rounded-lg border border-gray-200 hover:border-red-300 hover:bg-red-50 transition-colors text-sm"
            >
              <div className="w-4 h-4 text-red-600">🎥</div>
              <span className="text-gray-700">YouTube Analizi</span>
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="text-sm text-gray-500 pt-8 border-t border-gray-200">
          <p>
            Hala aradığınızı bulamıyor musunuz?{" "}
            <Button 
              variant="link" 
              className="h-auto p-0 text-blue-600 hover:text-blue-800"
              onClick={() => window.history.back()}
            >
              <ArrowLeft className="w-3 h-3 mr-1" />
              Geri dön
            </Button>
            {" "}veya ana sayfadan başlayın.
          </p>
        </div>
      </div>
    </div>
  );
}