"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import Image from "next/image"
import { Send } from "lucide-react"
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
}

export function TrendSpotterChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
    }

    setMessages((prev) => [...prev, newMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await fetch("https://trendspotter-server.onrender.com/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages: [...messages, newMessage] }), // Send all messages including the new one
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const botResponseMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: data.role as "assistant", // Ensure role is 'assistant'
        content: data.content,
      }
      setMessages((prev) => [...prev, botResponseMessage])
    } catch (error) {
      console.error("Error sending message to backend:", error)
      // Optionally, add an error message to the chat
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Oops! Something went wrong. Please try again.",
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-[#8544CE] flex flex-col relative overflow-hidden font-sans">
      <div className="fixed top-0 left-0 right-0 z-50 bg-[#8544CE]">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between relative h-32">
          <button
            onClick={() => setMessages([])}
            className="bg-[#2DD4BF] hover:bg-[#26b8a5] text-white px-5 py-2 rounded-full font-semibold text-base transition-colors shadow-sm flex items-center gap-2 z-10"
          >
            New chat
          </button>

          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 md:w-52 md:h-52 mt-6">
            <Image
              src="/trend-spotter-logo.png"
              alt="Trend Spotter Logo"
              fill
              className="object-contain drop-shadow-md"
              priority
            />
          </div>
        </div>
      </div>

      <main className="flex-1 flex flex-col items-center justify-start w-full max-w-5xl mx-auto px-4 pb-32 pt-36">
        {/* Chat Area / Placeholder */}
        <div className="w-full max-w-3xl relative">
          {messages.length === 0 ? (
            // Empty State Placeholder (The grey box from the design)
            <div className="bg-white/20 backdrop-blur-sm rounded-3xl h-48 w-full md:w-2/3 ml-auto hidden md:block animate-in fade-in slide-in-from-bottom-4 duration-700">
              {/* This replicates the empty grey box in the design */}
            </div>
          ) : (
            // Active Chat Messages
            <div className="space-y-4 w-full h-[400px] overflow-y-auto pr-4 custom-scrollbar">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn("flex w-full", message.role === "user" ? "justify-end" : "justify-start")}
                >
                  <div
                    className={cn(
                      "max-w-[80%] rounded-2xl px-6 py-4 text-xl shadow-md font-sans", // Changed text-lg to text-xl and added font-sans
                      message.role === "user"
                        ? "bg-[#FDE047] text-black rounded-br-none" // Yellow for user
                        : "bg-white text-gray-800 rounded-bl-none", // White for assistant
                    )}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white rounded-2xl rounded-bl-none px-6 py-4 shadow-md">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Footer / Input Area */}
      <div className="fixed bottom-0 left-0 right-0 p-6 pb-10 bg-gradient-to-t from-[#8544CE] via-[#8544CE] to-transparent z-20">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          {/* Send Button (Yellow Circle) */}
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="flex-shrink-0 w-14 h-14 bg-[#FDE047] hover:bg-[#fcd34d] rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            <Send className="w-6 h-6 text-black fill-black ml-1 group-hover:translate-x-0.5 transition-transform" />
          </button>

          {/* Input Field */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Let's go viral. What should we track?"
              className="w-full bg-[#E5E7EB] text-gray-800 placeholder:text-gray-500 text-xl px-8 py-4 rounded-full focus:outline-none focus:ring-2 focus:ring-[#FDE047] shadow-inner"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
