import React from "react";
import { RiRobot2Line } from "react-icons/ri";
import { GoCopy } from "react-icons/go";
import { FaGithub } from "react-icons/fa";
import { ChartColumn } from "lucide-react";
import { useUser } from "@clerk/nextjs";
import { Reference } from "../../../models/chat";
import { Spinner } from "../../ui/shadcn-io/spinner";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "../../ui/hover-card";
import { ChatReasoning } from "./chat-reasoning";
import {
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from "../../ui/shadcn-io/ai/reasoning";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant" | "github" | "statistics";
  timestamp: Date | string; // Allow both Date and string for formatted timestamps
  references?: Reference[];
}

interface ChatMessageProps {
  messages: Message[];
  isLoading: boolean;
  userAvatarUrl?: string;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  onSpanSelect?: (spanId: string) => void;
  onViewTypeChange?: (viewType: "log" | "agent" | "trace") => void;
  chatId?: string | null;
}

// Helper function to format timestamp like in LogDetail
const formatTimestamp = (timestamp: Date | string) => {
  const date = typeof timestamp === "string" ? new Date(timestamp) : timestamp;

  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  // The API returns UTC datetime values, but Date object methods like getFullYear()
  // automatically convert to local timezone, which is what we want for display
  const y = date.getFullYear();
  const m = months[date.getMonth()];
  const d = date.getDate();
  const h = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
  const s = String(date.getSeconds()).padStart(2, "0");

  // Add ordinal suffix to day
  const getOrdinalSuffix = (day: number) => {
    if (day >= 11 && day <= 13) return "th";
    switch (day % 10) {
      case 1:
        return "st";
      case 2:
        return "nd";
      case 3:
        return "rd";
      default:
        return "th";
    }
  };

  return `${y} ${m} ${d}${getOrdinalSuffix(d)} ${h}:${min}:${s}`;
};

// Helper function to get log level colors
const getLogLevelColor = (level: string) => {
  switch (level) {
    case "CRITICAL":
      return "font-medium text-[#7f1d1d]";
    case "ERROR":
      return "font-medium text-[#dc2626]";
    case "WARNING":
      return "font-medium text-[#fb923c]";
    case "INFO":
      return "font-medium text-[#64748b]";
    case "DEBUG":
      return "font-medium text-[#a855f7]";
    default:
      return "font-medium text-[#64748b]";
  }
};

// Simple markdown renderer for basic formatting
const renderMarkdown = (
  text: string,
  messageId: string,
  references?: Reference[],
  onSpanSelect?: (spanId: string) => void,
  onViewTypeChange?: (viewType: "log" | "agent" | "trace") => void,
  openHoverCard?: string | null,
  setOpenHoverCard?: (id: string | null) => void,
): React.ReactNode => {
  let currentIndex = 0;
  // Patterns for markdown elements (order matters - code blocks should be processed first)
  const patterns = [
    // PR created pattern - MUST be first to catch it before other patterns
    {
      regex:
        /PR created:\s*https:\/\/github\.com\/([^\/\s]+)\/([^\/\s]+)\/pull\/(\d+)/g,
      component: (match: string, ...args: string[]) => {
        const owner = args[0];
        const repo = args[1];
        const pullNumber = args[2];
        const fullUrl = `https://github.com/${owner}/${repo}/pull/${pullNumber}`;

        return (
          <span key={currentIndex++}>
            PR created:{" "}
            <a
              href={fullUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-black dark:text-white hover:text-gray-600 dark:hover:text-gray-300 underline font-medium transition-colors"
              title={`${owner}/${repo} Pull Request #${pullNumber}`}
            >
              PR #{pullNumber}
            </a>
          </span>
        );
      },
    },
    // Handle literal triple backticks (when not containing code content)
    {
      regex: /```(?!\w)(?!\n[\s\S]*?```)/g,
      component: (match: string, ...args: string[]) => (
        <span key={currentIndex++}>{match}</span>
      ),
    },
    // Handle code blocks with content
    {
      regex: /```(\w+)?\n?([\s\S]*?)```/g,
      component: (match: string, ...args: string[]) => {
        // For code blocks: args[0] might be language, args[1] is content
        // If no language specified, args[0] is content
        const content = args.length > 1 ? args[1] : args[0];
        const trimmedContent = content.trim();

        // If content is empty or just whitespace, treat as literal backticks
        if (!trimmedContent) {
          return <span key={currentIndex++}>{match}</span>;
        }

        const handleCopy = async () => {
          try {
            await navigator.clipboard.writeText(trimmedContent);
          } catch (err) {
            console.error("Failed to copy text: ", err);
          }
        };

        return (
          <pre
            key={currentIndex++}
            className="bg-gray-100 dark:bg-zinc-800 border border-gray-300 dark:border-zinc-600 rounded-md p-3 my-2 overflow-x-auto relative group"
          >
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-400"
              title="Copy code"
            >
              <GoCopy className="w-4 h-4" />
            </button>
            <code className="text-xs font-mono text-gray-800 dark:text-gray-200 whitespace-pre">
              {trimmedContent}
            </code>
          </pre>
        );
      },
    },
    // GitHub pull request URL pattern - process before issues to avoid conflicts
    {
      regex: /https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/pull\/(\d+)/g,
      component: (match: string, ...args: string[]) => {
        const [owner, repo, pullNumber] = args;
        const fullUrl = match;

        return (
          <a
            key={currentIndex++}
            href={fullUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-black dark:text-white hover:text-gray-600 dark:hover:text-gray-300 underline font-medium transition-colors"
            title={`${owner}/${repo} Pull Request #${pullNumber}`}
          >
            PR #{pullNumber}
          </a>
        );
      },
    },
    // GitHub issue URL pattern - should be processed early to avoid conflicts with other link patterns
    {
      regex: /https:\/\/github\.com\/([^\/]+)\/([^\/]+)\/issues\/(\d+)/g,
      component: (match: string, ...args: string[]) => {
        const [owner, repo, issueNumber] = args;
        const fullUrl = match;

        return (
          <a
            key={currentIndex++}
            href={fullUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-black dark:text-white hover:text-gray-600 dark:hover:text-gray-300 underline font-medium transition-colors"
            title={`${owner}/${repo} Issue #${issueNumber}`}
          >
            #{issueNumber}
          </a>
        );
      },
    },
    // Standard markdown link pattern - [text](url)
    {
      regex: /\[([^\]]+)\]\(([^)]+)\)/g,
      component: (match: string, ...args: string[]) => {
        const [linkText, url] = args;

        return (
          <a
            key={currentIndex++}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-black dark:text-white hover:text-gray-600 dark:hover:text-gray-300 underline font-medium transition-colors"
            title={linkText}
          >
            {linkText}
          </a>
        );
      },
    },
    // Reference numbers pattern - must come before log level patterns
    {
      regex: /\[(\d+)\]/g,
      component: (match: string, ...args: string[]) => {
        const refNumber = parseInt(args[0]);
        const reference = references?.find((ref) => ref.number === refNumber);

        if (reference) {
          // Create unique ID for each reference instance by including currentIndex
          const hoverCardId = `${messageId}-ref-${refNumber}-${currentIndex}`;
          return (
            <HoverCard
              key={currentIndex++}
              open={openHoverCard === hoverCardId}
              onOpenChange={(open) =>
                setOpenHoverCard?.(open ? hoverCardId : null)
              }
            >
              <HoverCardTrigger asChild>
                <span className="cursor-pointer text-black dark:text-white font-medium underline hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                  {match}
                </span>
              </HoverCardTrigger>
              <HoverCardContent className="w-80">
                <div className="space-y-2">
                  {reference.span_id && (
                    <div>
                      <span className="font-semibold text-sm">Span ID:</span>{" "}
                      <button
                        onClick={(e) => {
                          // Prevent event bubbling
                          e.preventDefault();
                          e.stopPropagation();

                          // Force close the hover card immediately to prevent popup persistence
                          setOpenHoverCard?.(null);

                          // Small delay to ensure hover card closes completely before view switch
                          // This prevents visual artifacts during the transition
                          setTimeout(() => {
                            onSpanSelect?.(reference.span_id!);
                            onViewTypeChange?.("log");
                          }, 100);
                        }}
                        className="text-sm text-black dark:text-white hover:text-gray-700 dark:hover:text-gray-300 underline cursor-pointer transition-colors"
                        title="Click to select this span and switch to log view"
                      >
                        {reference.span_id}
                      </button>
                    </div>
                  )}
                  {reference.span_function_name && (
                    <div>
                      <span className="font-semibold text-sm">Function:</span>{" "}
                      <span className="text-sm break-all">
                        {reference.span_function_name}
                      </span>
                    </div>
                  )}
                  {reference.line_number && (
                    <div>
                      <span className="font-semibold text-sm">Line:</span>{" "}
                      <span className="text-sm">{reference.line_number}</span>
                    </div>
                  )}
                  {reference.log_message && (
                    <div>
                      <span className="font-semibold text-sm">Log:</span>
                      <div className="mt-1 p-2 bg-muted rounded text-xs font-mono whitespace-pre-wrap max-h-40 overflow-auto">
                        {reference.log_message}
                      </div>
                    </div>
                  )}
                </div>
              </HoverCardContent>
            </HoverCard>
          );
        } else {
          // Fallback for references without data - simple span without hover card
          return (
            <span
              key={currentIndex++}
              className="text-black dark:text-white font-medium underline opacity-50 font-sans"
              style={{ textDecoration: "underline" }}
              title={`No reference data found for [${refNumber}]`}
            >
              {match}
            </span>
          );
        }
      },
    },
    // Log level patterns - must come before headers to avoid conflicts
    {
      regex: /\b(CRITICAL|ERROR|WARNING|INFO|DEBUG)\b/g,
      component: (match: string, ...args: string[]) => (
        <span key={currentIndex++} className={getLogLevelColor(args[0])}>
          {args[0]}
        </span>
      ),
    },
    // Header patterns
    {
      regex: /###\s+([^\n]+)/g,
      component: (match: string, ...args: string[]) => (
        <h3
          key={currentIndex++}
          className="text-lg font-bold text-gray-900 dark:text-gray-100 my-1"
        >
          {renderMarkdown(
            args[0],
            messageId,
            references,
            onSpanSelect,
            onViewTypeChange,
          )}
        </h3>
      ),
    },
    {
      regex: /##\s+([^\n]+)/g,
      component: (match: string, ...args: string[]) => (
        <h2
          key={currentIndex++}
          className="text-xl font-bold text-gray-900 dark:text-gray-100 my-1"
        >
          {renderMarkdown(
            args[0],
            messageId,
            references,
            onSpanSelect,
            onViewTypeChange,
          )}
        </h2>
      ),
    },
    {
      regex: /#\s+([^\n]+)/g,
      component: (match: string, ...args: string[]) => (
        <h1
          key={currentIndex++}
          className="text-2xl font-bold text-gray-900 dark:text-gray-100 my-1"
        >
          {renderMarkdown(
            args[0],
            messageId,
            references,
            onSpanSelect,
            onViewTypeChange,
          )}
        </h1>
      ),
    },
    {
      regex: /\*\*(.*?)\*\*/g,
      component: (match: string, ...args: string[]) => (
        <strong key={currentIndex++}>
          {renderMarkdown(
            args[0],
            messageId,
            references,
            onSpanSelect,
            onViewTypeChange,
          )}
        </strong>
      ),
    },
    {
      regex: /\*(.*?)\*/g,
      component: (match: string, ...args: string[]) => (
        <em key={currentIndex++}>
          {renderMarkdown(
            args[0],
            messageId,
            references,
            onSpanSelect,
            onViewTypeChange,
          )}
        </em>
      ),
    },
    {
      regex: /`(.*?)`/g,
      component: (match: string, ...args: string[]) => (
        <code
          key={currentIndex++}
          className="bg-gray-100 dark:bg-zinc-600 px-1 py-0.5 rounded text-xs font-mono"
        >
          {args[0]}
        </code>
      ),
    },
  ];

  let remainingText = text;
  const elements: React.ReactNode[] = [];

  while (remainingText.length > 0) {
    let earliestMatch = null;
    let earliestIndex = remainingText.length;
    let matchingPattern = null;

    // Find the earliest pattern match
    for (const pattern of patterns) {
      const match = pattern.regex.exec(remainingText);
      if (match && match.index < earliestIndex) {
        earliestMatch = match;
        earliestIndex = match.index;
        matchingPattern = pattern;
      }
    }

    if (earliestMatch && matchingPattern) {
      // Add text before the match
      if (earliestIndex > 0) {
        elements.push(remainingText.substring(0, earliestIndex));
      }

      // Add the formatted element
      elements.push(
        matchingPattern.component(earliestMatch[0], ...earliestMatch.slice(1)),
      );

      // Update remaining text
      remainingText = remainingText.substring(
        earliestIndex + earliestMatch[0].length,
      );

      // Reset regex lastIndex for next iteration
      patterns.forEach((p) => (p.regex.lastIndex = 0));
    } else {
      // No more matches, add remaining text
      elements.push(remainingText);
      break;
    }
  }

  return elements.length > 0 ? elements : text;
};

export default function ChatMessage({
  messages,
  isLoading,
  userAvatarUrl,
  messagesEndRef,
  onSpanSelect,
  onViewTypeChange,
  chatId,
}: ChatMessageProps) {
  const { user } = useUser();
  const avatarLetter =
    user?.emailAddresses?.[0]?.emailAddress?.charAt(0)?.toUpperCase() || "U";
  // State to control all hover cards in this component
  // We need controlled state to programmatically close hover cards when clicking span links
  // This prevents the popup from persisting and moving to the left panel during view transitions
  const [openHoverCard, setOpenHoverCard] = React.useState<string | null>(null);

  return (
    <div className="flex-1 overflow-y-auto p-4 flex flex-col bg-zinc-50 dark:bg-zinc-900 mt-2 ml-4 mr-4 mb-2 rounded-lg">
      <div className="flex-1"></div>
      {messages.map((message, index) => {
        // Show reasoning after every user message
        const shouldShowReasoning = message.role === "user";

        // Find the next assistant message timestamp for upper bound filtering
        const nextAssistantMessage = messages
          .slice(index + 1)
          .find((msg) => msg.role === "assistant");
        const nextMessageTimestamp = nextAssistantMessage?.timestamp;

        return (
          <React.Fragment key={message.id}>
            <div
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              } mb-4 items-start gap-2`}
            >
              {/* Avatar for assistant, github, and statistics */}
              {(message.role === "assistant" ||
                message.role === "github" ||
                message.role === "statistics") && (
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-zinc-600 dark:bg-zinc-200 border border-zinc-600 dark:border-zinc-200`}
                >
                  {message.role === "github" ? (
                    <FaGithub className="w-5 h-5 text-white dark:text-zinc-600" />
                  ) : message.role === "statistics" ? (
                    <ChartColumn className="w-5 h-5 text-white dark:text-zinc-600" />
                  ) : (
                    <RiRobot2Line className="w-5 h-5 text-white dark:text-zinc-600" />
                  )}
                </div>
              )}

              {/* Message content */}
              <div
                className={`max-w-[70%] max-w-[600px] rounded-lg px-4 py-2 break-words ${
                  message.role === "user"
                    ? "bg-white dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border border-zinc-300 dark:border-zinc-700"
                    : message.role === "github"
                      ? "bg-white dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border border-zinc-300 dark:border-zinc-700"
                      : message.role === "statistics"
                        ? "bg-white dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border border-zinc-300 dark:border-zinc-700"
                        : "bg-white dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border border-zinc-300 dark:border-zinc-700"
                }`}
              >
                <div className="whitespace-pre-wrap break-words text-sm">
                  {renderMarkdown(
                    message.content,
                    message.id,
                    message.references,
                    onSpanSelect,
                    onViewTypeChange,
                    openHoverCard,
                    setOpenHoverCard,
                  )}
                </div>
                <p className="text-xs mt-1 opacity-70">
                  {formatTimestamp(message.timestamp)}
                </p>
              </div>

              {/* Avatar for user */}
              {message.role === "user" && (
                <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0">
                  {userAvatarUrl ? (
                    <img
                      src={userAvatarUrl}
                      alt="User avatar"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-sidebar-accent/50 flex items-center justify-center bg-zinc-200 dark:bg-zinc-800">
                      <span className="text-sidebar-accent-foreground font-semibold text-sm">
                        {avatarLetter || "U"}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Show reasoning after user messages */}
            {shouldShowReasoning && (
              <div className="mb-4">
                {chatId ? (
                  <ChatReasoning
                    chatId={chatId}
                    className="w-full"
                    isLoading={isLoading}
                    userMessageTimestamp={message.timestamp}
                    nextMessageTimestamp={nextMessageTimestamp}
                  />
                ) : (
                  <Reasoning
                    className="w-full"
                    isStreaming={isLoading}
                    defaultOpen={true}
                  >
                    <ReasoningTrigger />
                    <ReasoningContent>{"Processing..."}</ReasoningContent>
                  </Reasoning>
                )}
              </div>
            )}
          </React.Fragment>
        );
      })}
      {/* Loading indicator */}
      {isLoading && (
        <div className="flex justify-start mb-4 items-start gap-2">
          <div className="w-8 h-8 rounded-full bg-zinc-700 dark:bg-zinc-200 flex items-center justify-center flex-shrink-0 animate-pulse">
            <RiRobot2Line className="w-5 h-5 text-white dark:text-zinc-700" />
          </div>
          <div className="flex items-center justify-center py-1 px-2">
            <Spinner
              variant="infinite"
              className="w-7 h-7 text-gray-500 dark:text-gray-400"
            />
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
