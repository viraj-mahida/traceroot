'use client'

import React, { useState } from 'react';
import { GoArrowRight, GoArrowUpRight } from 'react-icons/go';
import { BsLightning } from "react-icons/bs";
import { RiRobot2Line } from "react-icons/ri";
import { FaCode } from "react-icons/fa6";
import Link from 'next/link';
import { shouldShowPaymentFeatures } from '@/utils/stripe-config';

export default function Home() {
  const [isDocsHovered, setIsDocsHovered] = useState(false);
  const [isContactHovered, setIsContactHovered] = useState(false);
  const [isConnectHovered, setIsConnectHovered] = useState(false);
  const [isQuickstartHovered, setIsQuickstartHovered] = useState(false);
  const [isMonitorHovered, setIsMonitorHovered] = useState(false);
  const [isSettingsHovered, setIsSettingsHovered] = useState(false);

  const showPaymentFeatures = shouldShowPaymentFeatures();

  return (
    <div className="min-h-screen flex items-center justify-center relative">
      {/* Top right buttons */}
      <div className="absolute top-6 right-6 flex gap-4">
        <button
          className="w-auto px-6 py-3 bg-white hover:bg-green-50 backdrop-blur-xl text-gray-800 hover:text-green-700 font-semibold transition-all duration-200 rounded-md border border-gray-300/50"
          onClick={() => window.open('https://cal.com/traceroot/30min', '_blank')}
          onMouseEnter={() => setIsContactHovered(true)}
          onMouseLeave={() => setIsContactHovered(false)}
        >
          <span className="flex items-center gap-2">
            Contact Us
            <span className="transition-transform duration-600 ease-in-out">
              {isContactHovered ? (
                <GoArrowRight className="w-4 h-4 animate-pulse" />
              ) : (
                <GoArrowUpRight className="w-4 h-4" />
              )}
            </span>
          </span>
        </button>
        <button
          className="w-auto px-6 py-3 bg-white hover:bg-green-50 backdrop-blur-xl text-gray-800 hover:text-green-700 font-semibold transition-all duration-200 rounded-md border border-gray-300/50"
          onClick={() => window.open('https://docs.traceroot.ai', '_blank')}
          onMouseEnter={() => setIsDocsHovered(true)}
          onMouseLeave={() => setIsDocsHovered(false)}
        >
          <span className="flex items-center gap-2">
            Docs
            <span className="transition-transform duration-600 ease-in-out">
              {isDocsHovered ? (
                <GoArrowRight className="w-4 h-4 animate-pulse" />
              ) : (
                <GoArrowUpRight className="w-4 h-4" />
              )}
            </span>
          </span>
        </button>
      </div>

      {/* Main content */}
      <div className="text-center px-6 max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-5xl md:text-6xl font-bold text-black dark:text-black mb-6 leading-tight">
            TraceRoot.AI
          </h1>
          <div className="text-2xl md:text-3xl font-light text-black dark:text-black mb-8 leading-relaxed">
            Agentic debugging made <span className="font-bold text-green-600">simple</span>
          </div>
        </div>

        <div className="space-y-8 max-w-4xl mx-auto">
          <p className="text-xl text-black dark:text-black leading-relaxed">
            A platform for understanding application performance and debugging issues with AI agents
          </p>

          <div className="grid gap-6 md:gap-8 mt-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl p-6 border border-blue-200/50 hover:shadow-lg transition-all duration-300 hover:scale-105">
                <div className="flex items-center justify-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                    <RiRobot2Line className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-800">AI Powered</h3>
                </div>
                <p className="text-gray-700 text-sm leading-relaxed">
                  Customized AI agents that can answer any questions about the trace, logs, and more
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100/50 rounded-xl p-6 border border-purple-200/50 hover:shadow-lg transition-all duration-300 hover:scale-105">
                <div className="flex items-center justify-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                    <FaCode className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-800">Multiple Types</h3>
                </div>
                <p className="text-gray-700 text-sm leading-relaxed">
                  Support systems such as microservices, voice agents, and multi-agent systems
                </p>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100/50 rounded-xl p-6 border border-green-200/50 hover:shadow-lg transition-all duration-300 hover:scale-105">
                <div className="flex items-center justify-center gap-3 mb-3">
                  <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                    <BsLightning className="w-5 h-5 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-800">Fast & Easy</h3>
                </div>
                <p className="text-gray-700 text-sm leading-relaxed">
                  Set up in minutes with our intuitive interface and get instant insights
                </p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-gray-50 to-white rounded-xl p-2 border border-gray-200/50 mb-6">
              <p className="text-gray-800 text-md">
                Connect to your applications securely by visiting &nbsp;
                <Link
                  href="/integrate"
                  className="inline-flex items-center gap-2 font-bold text-blue-600 hover:text-blue-700 underline decoration-blue-600/30 hover:decoration-blue-700 transition-all duration-200"
                  onMouseEnter={() => setIsConnectHovered(true)}
                  onMouseLeave={() => setIsConnectHovered(false)}
                >
                  Navigate to Integrate
                  <span className="transition-transform duration-600 ease-in-out">
                    {isConnectHovered ? (
                      <GoArrowRight className="w-4 h-4 animate-pulse" />
                    ) : (
                      <GoArrowUpRight className="w-4 h-4" />
                    )}
                  </span>
                </Link>
              </p>
            </div>

            <div className="bg-gradient-to-r from-green-50 to-green-100/50 rounded-xl p-2 border border-green-200/50 mb-6">
              <p className="text-gray-800 text-md">
                Start monitoring by visiting &nbsp;
                <Link
                  href="/explore"
                  className="inline-flex items-center gap-2 font-bold text-green-600 hover:text-green-700 underline decoration-green-600/30 hover:decoration-green-700 transition-all duration-200"
                  onMouseEnter={() => setIsMonitorHovered(true)}
                  onMouseLeave={() => setIsMonitorHovered(false)}
                >
                  Navigate to Explore
                  <span className="transition-transform duration-600 ease-in-out">
                    {isMonitorHovered ? (
                      <GoArrowRight className="w-4 h-4 animate-pulse" />
                    ) : (
                      <GoArrowUpRight className="w-4 h-4" />
                    )}
                  </span>
                </Link>
              </p>
            </div>

            {/* Only show settings link if Stripe is configured */}
            {showPaymentFeatures && (
              <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-2 border border-orange-200/50 mb-6">
                <p className="text-gray-800 text-md">
                  Manage your account and subscription settings by visiting &nbsp;
                  <Link
                    href="/settings"
                    className="inline-flex items-center gap-2 font-bold text-orange-600 hover:text-orange-700 underline decoration-orange-600/30 hover:decoration-orange-700 transition-all duration-200"
                    onMouseEnter={() => setIsSettingsHovered(true)}
                    onMouseLeave={() => setIsSettingsHovered(false)}
                  >
                    Navigate to Settings
                    <span className="transition-transform duration-600 ease-in-out">
                      {isSettingsHovered ? (
                        <GoArrowRight className="w-4 h-4 animate-pulse" />
                      ) : (
                        <GoArrowUpRight className="w-4 h-4" />
                      )}
                    </span>
                  </Link>
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
