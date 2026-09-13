import React, { useState, useEffect, useRef } from 'react';
import { Language, ThemeMode, PersonaProfile, ChatMessage } from '../types';
import { translations } from '../data/translations';
import {
  Bot,
  Mic,
  Send,
  Volume2,
  VolumeX,
  CheckCircle2,
  Sparkles,
  ShieldCheck,
  ArrowRight,
  Square
} from 'lucide-react';

interface SakhiChatWindowProps {
  activePersona: PersonaProfile;
  lang: Language;
  theme: ThemeMode;
  initialPrompt?: string;
  onClearInitialPrompt?: () => void;
}

export const SakhiChatWindow: React.FC<SakhiChatWindowProps> = ({
  activePersona,
  lang,
  theme,
  initialPrompt,
  onClearInitialPrompt,
}) => {
  const t = translations[lang];
  const isDark = theme === 'dark';
  const isTiranga = !isDark;
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const [inputVal, setInputVal] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const speechRecognitionRef = useRef<any>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Initial messages customized to active persona
  const initialMessages: ChatMessage[] = [
    {
      id: 'msg-1',
      sender: 'sakhi',
      text: `Namaste ${activePersona.name}! I am Sakhi, your personal digital banking assistant. I am here to assist you with quick loan applications, simplified video KYC, or any banking questions in your preferred language.`,
      hindiText: `नमस्ते ${activePersona.hindiName} जी! मैं सखी हूँ, आपकी व्यक्तिगत डिजिटल बैंकिंग साथी। मैं यहाँ आपकी भाषा में आसान ऋण आवेदन, सरल वीडियो केवाईसी और बैंकिंग सहायता के लिए उपलब्ध हूँ।`,
      timestamp: 'Just now',
      audioText: lang === 'en'
        ? `Namaste ${activePersona.name}! I am Sakhi, your personal banking companion.`
        : `नमस्ते ${activePersona.hindiName} जी! मैं सखी हूँ, आपकी व्यक्तिगत बैंकिंग साथी।`,
      suggestedActions: [
        {
          label: 'Apply for Pre-Approved Capital',
          hindiLabel: 'पूर्व-स्वीकृत ऋण हेतु आवेदन',
          actionId: 'apply_loan',
        },
        {
          label: 'How does Video KYC work?',
          hindiLabel: 'वीडियो केवाईसी कैसे करें?',
          actionId: 'explain_kyc',
        },
        {
          label: 'Check Interest Rates & Fees',
          hindiLabel: 'ब्याज दर व कोई शुल्क तो नहीं?',
          actionId: 'check_charges',
        },
      ],
    },
  ];

  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);

  // Sync if persona changes
  useEffect(() => {
    setMessages([
      {
        id: `msg-${Date.now()}`,
        sender: 'sakhi',
        text: `Swagatam ${activePersona.name}! I am Sakhi. How can I help you today with your ${activePersona.occupation} account?`,
        hindiText: `स्वागतम ${activePersona.hindiName} जी! मैं सखी हूँ। मैं आज आपके खाते एवं व्यवसाय के लिए किस प्रकार सहायता कर सकती हूँ?`,
        timestamp: 'Just now',
        audioText: lang === 'en'
          ? `Welcome ${activePersona.name}! Ask me anything in Hindi or English.`
          : `स्वागतम ${activePersona.hindiName} जी! आप मुझसे कुछ भी पूछ सकते हैं।`,
        suggestedActions: [
          {
            label: 'Start 2-Minute Loan Sanction',
            hindiLabel: '2 मिनट में ऋण स्वीकृति शुरू करें',
            actionId: 'apply_loan',
          },
          {
            label: 'Step-by-step Video KYC Guide',
            hindiLabel: 'केवाईसी की आसान प्रक्रिया',
            actionId: 'explain_kyc',
          },
        ],
      },
    ]);
  }, [activePersona.id]);

  // Handle external initial prompt if passed from dashboard
  useEffect(() => {
    if (initialPrompt) {
      handleUserQuery(initialPrompt);
      if (onClearInitialPrompt) onClearInitialPrompt();
    }
  }, [initialPrompt]);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Text-To-Speech function using Browser SpeechSynthesis
  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();
    if (isSpeaking) {
      setIsSpeaking(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'en' ? 'en-IN' : 'hi-IN';
    utterance.rate = 0.95;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  const handleUserQuery = async (queryText: string) => {
    if (!queryText.trim()) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputVal('');

    try {
      const response = await import('../services/api').then(m => m.chatWithSakhi(activePersona.id, queryText));
      
      const botResponse: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'sakhi',
        text: response.reply,
        hindiText: response.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        audioText: response.reply,
      };
      
      setMessages((prev) => [...prev, botResponse]);
      speakText(response.reply);
    } catch (error) {
      const errorMsg: ChatMessage = {
        id: `bot-err-${Date.now()}`,
        sender: 'sakhi',
        text: 'Sorry, I am having trouble connecting to the server. Please try again later.',
        hindiText: 'क्षमा करें, मुझे सर्वर से जुड़ने में परेशानी हो रही है। कृपया बाद में पुनः प्रयास करें।',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        audioText: 'Sorry, there was an error processing your request.',
      };
      setMessages((prev) => [...prev, errorMsg]);
      speakText('Sorry, there was an error processing your request.');
    }
  };

  const cleanupRecording = () => {
    setIsRecording(false);
    if (speechRecognitionRef.current) {
      try {
        speechRecognitionRef.current.onend = null;
        speechRecognitionRef.current.onerror = null;
        speechRecognitionRef.current.stop();
      } catch (e) {
        // ignore
      }
      speechRecognitionRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (e) {
        // ignore
      }
      mediaRecorderRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      cleanupRecording();
    };
  }, []);

  const toggleRecording = async () => {
    if (isRecording) {
      cleanupRecording();
      return;
    }

    // 1. Check browser microphone support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const errorText = lang === 'en'
        ? 'Microphone recording is not supported in this browser.'
        : 'इस ब्राउज़र में माइक्रोफ़ोन समर्थित नहीं है।';
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'sakhi',
          text: errorText,
          hindiText: errorText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
      return;
    }

    // 2. Check SpeechRecognition support
    const SpeechRecognitionClass =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      const errorText = lang === 'en'
        ? 'Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.'
        : 'इस ब्राउज़र में वाक् पहचान समर्थित नहीं है। कृपया Chrome या Edge का उपयोग करें।';
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'sakhi',
          text: errorText,
          hindiText: errorText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
      return;
    }

    try {
      // 3. Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // 4. Record actual microphone audio using MediaRecorder
      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;

      // 5. Speech-to-text conversion
      const recognition = new SpeechRecognitionClass();
      recognition.lang = lang === 'en' ? 'en-IN' : 'hi-IN';
      recognition.continuous = false;
      recognition.interimResults = false;

      let recognizedTranscript = '';

      recognition.onresult = (event: any) => {
        const transcript = event.results[0]?.[0]?.transcript || '';
        if (transcript.trim()) {
          recognizedTranscript = transcript.trim();
        }
      };

      recognition.onerror = (event: any) => {
        cleanupRecording();
        if (event.error === 'no-speech') {
          const noSpeechMsg = lang === 'en'
            ? 'No speech was detected. Please try speaking again.'
            : 'कोई आवाज़ सुनाई नहीं दी। कृपया पुनः प्रयास करें।';
          setMessages((prev) => [
            ...prev,
            {
              id: `bot-err-${Date.now()}`,
              sender: 'sakhi',
              text: noSpeechMsg,
              hindiText: noSpeechMsg,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
        }
      };

      recognition.onend = () => {
        cleanupRecording();
        if (recognizedTranscript) {
          handleUserQuery(recognizedTranscript);
        }
      };

      speechRecognitionRef.current = recognition;
      recognition.start();
      setIsRecording(true);
    } catch (err: any) {
      cleanupRecording();
      let errorMsg = lang === 'en'
        ? 'Could not access the microphone. Please check permissions.'
        : 'माइक्रोफ़ोन तक पहुँच नहीं हो सकी। कृपया अनुमति जाँचें।';
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMsg = lang === 'en'
          ? 'Microphone permission was denied. Please allow microphone access in your browser settings.'
          : 'माइक्रोफ़ोन अनुमति अस्वीकार कर दी गई। कृपया ब्राउज़र सेटिंग्स में माइक्रोफ़ोन की अनुमति दें।';
      }
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-err-${Date.now()}`,
          sender: 'sakhi',
          text: errorMsg,
          hindiText: errorMsg,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  };

  return (
    <div className="space-y-3 animate-fade-in flex flex-col h-[700px]">
      {/* Top Header Card */}
      <div
        className={`p-3 rounded-2xl border transition-colors ${
          isTiranga
            ? 'bg-gradient-to-r from-[#FFF5EB] via-white to-[#F0FDF4] border-[#FF671F]/30 text-slate-900 shadow-sm border-t-2 border-t-[#FF671F]'
            : isDark
            ? 'bg-[#0E1526] border-slate-800 text-slate-100'
            : 'bg-white border-slate-200 text-slate-900 shadow-sm'
        }`}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center text-white font-bold shadow-sm ${
                isTiranga ? 'bg-[#FF671F]' : 'bg-blue-600'
              }`}
            >
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h3
                className={`font-bold text-xs sm:text-sm flex items-center gap-1.5 ${
                  isTiranga ? 'text-slate-950' : isDark ? 'text-white' : 'text-slate-950'
                }`}
              >
                <span>{t.sakhiTitle}</span>
                <span className="w-2 h-2 rounded-full bg-[#046A38] animate-pulse" />
              </h3>
              <p
                className={`text-[11px] ${
                  isDark ? 'text-slate-400' : 'text-slate-600'
                }`}
              >
                {t.sakhiSubtitle}
              </p>
            </div>
          </div>

          {isSpeaking && (
            <button
              onClick={stopSpeech}
              className="h-8 px-2.5 rounded-xl bg-red-500/10 text-red-500 hover:bg-red-500/20 text-xs font-bold inline-flex items-center gap-1.5 transition-colors"
              title="Stop Voice"
            >
              <VolumeX className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Stop Voice</span>
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div
        className={`flex-1 p-3.5 rounded-2xl border overflow-y-auto space-y-3.5 ${
          isDark
            ? 'bg-[#080B12] border-slate-800'
            : 'bg-slate-50/80 border-slate-200'
        }`}
      >
        {messages.map((msg) => {
          const isBot = msg.sender === 'sakhi';
          const displayText = lang === 'en' ? msg.text : (msg.hindiText || msg.text);

          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isBot ? 'items-start' : 'items-end'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed space-y-2 ${
                  isBot
                    ? isTiranga
                      ? 'bg-white border border-[#FF671F]/20 text-slate-900 shadow-sm'
                      : isDark
                      ? 'bg-[#0E1526] border border-slate-800 text-slate-100 shadow-sm'
                      : 'bg-white border border-slate-200 text-slate-900 shadow-sm'
                    : isTiranga
                    ? 'bg-gradient-to-r from-[#FF671F] to-[#E65100] text-white font-medium shadow-sm'
                    : 'bg-blue-600 text-white font-medium shadow-sm'
                }`}
              >
                <p className="leading-relaxed">{displayText}</p>

                {/* Step Card (Loan / KYC Progress) */}
                {msg.stepCard && (
                  <div
                    className={`p-2.5 rounded-xl border space-y-1 ${
                      isDark
                        ? 'bg-black/30 border-blue-500/30 text-slate-200'
                        : 'bg-blue-50/70 border-blue-200 text-slate-900'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[11px] flex items-center gap-1 text-blue-600 dark:text-blue-400">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                        <span>
                          {lang === 'en' ? msg.stepCard.title : msg.stepCard.hindiTitle}
                        </span>
                      </span>
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold">
                        {msg.stepCard.status === 'completed' ? 'Verified ✓' : 'In Progress'}
                      </span>
                    </div>
                    <p
                      className={`text-[10.5px] leading-relaxed ${
                        isDark ? 'text-slate-300' : 'text-slate-600'
                      }`}
                    >
                      {lang === 'en' ? msg.stepCard.details : msg.stepCard.hindiDetails}
                    </p>
                  </div>
                )}

                {/* Audio Playback Button */}
                {isBot && msg.audioText && (
                  <div className="pt-1 flex items-center justify-between border-t border-slate-200 dark:border-slate-800/60">
                    <button
                      onClick={() => speakText(msg.audioText || displayText)}
                      className={`text-[10.5px] font-semibold flex items-center gap-1 transition-colors ${
                        isDark ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-800'
                      }`}
                    >
                      <Volume2 className="w-3 h-3" />
                      <span>{isSpeaking ? t.stopAudio : t.listenAudio}</span>
                    </button>
                    <span
                      className={`text-[9px] ${
                        isDark ? 'text-slate-500' : 'text-slate-400'
                      }`}
                    >
                      {msg.timestamp}
                    </span>
                  </div>
                )}
              </div>

              {/* Action Chips */}
              {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2 max-w-[90%]">
                  {msg.suggestedActions.map((act, i) => (
                    <button
                      key={i}
                      onClick={() =>
                        handleUserQuery(lang === 'en' ? act.label : act.hindiLabel)
                      }
                      className={`h-8 px-3 rounded-xl border text-[11px] font-bold inline-flex items-center justify-center transition-all ${
                        isDark
                          ? 'bg-[#0E1526] border-slate-700 text-blue-300 hover:bg-slate-800'
                          : 'bg-white border-blue-200 text-blue-700 hover:bg-blue-50 shadow-sm'
                      }`}
                    >
                      {lang === 'en' ? act.label : act.hindiLabel} →
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
        <div ref={chatBottomRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div className="space-y-1">
        <span
          className={`text-[10.5px] font-medium px-1 ${
            isDark ? 'text-slate-400' : 'text-slate-500'
          }`}
        >
          {t.sampleVoicePrompts}
        </span>
        <div className="flex gap-1.5 overflow-x-auto pb-1 text-[11px] scrollbar-none">
          {[
            { en: 'How much interest on ₹25,000?', hi: '₹25,000 पर कितना ब्याज लगेगा?' },
            { en: 'Are there any hidden fees?', hi: 'क्या कोई छुपा हुआ शुल्क है?' },
            { en: 'How to complete Video KYC?', hi: 'वीडियो केवाईसी कैसे पूरी करें?' },
            { en: 'When is my payment due?', hi: 'मेरी अगली किस्त कब देय है?' },
          ].map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleUserQuery(lang === 'en' ? prompt.en : prompt.hi)}
              className={`h-8 px-3 rounded-xl border text-[11px] font-semibold transition-colors shrink-0 inline-flex items-center justify-center gap-1.5 whitespace-nowrap ${
                isDark
                  ? 'bg-slate-900 border-slate-800 text-slate-300 hover:text-white hover:border-slate-700'
                  : 'bg-white border-slate-300 text-slate-700 hover:text-slate-950 hover:bg-slate-50 shadow-sm'
              }`}
            >
              <span>💬</span>
              <span>{lang === 'en' ? prompt.en : prompt.hi}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Active Recording State Banner */}
      {isRecording && (
        <div className="flex items-center justify-center gap-2 py-1.5 px-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-400 text-xs animate-pulse">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
          <span className="font-semibold">
            {lang === 'en' ? 'Sakhi is listening... Speak your question' : 'सखी सुन रही हैं... अपना प्रश्न बोलें'}
          </span>
        </div>
      )}

      {/* Input Box */}
      <div
        className={`p-1.5 rounded-2xl border flex items-center gap-2 transition-all ${
          isRecording
            ? 'border-red-500 ring-2 ring-red-500/20'
            : isTiranga
            ? 'bg-white border-[#FF671F]/40 text-slate-900 shadow-sm'
            : isDark
            ? 'bg-[#0E1526] border-slate-800 text-slate-100'
            : 'bg-white border-slate-300 text-slate-900 shadow-sm'
        }`}
      >
        <button
          onClick={toggleRecording}
          type="button"
          className={`w-9 h-9 rounded-xl transition-all shrink-0 inline-flex items-center justify-center ${
            isRecording
              ? 'bg-red-600 text-white animate-pulse shadow-md shadow-red-500/40 hover:bg-red-700'
              : isTiranga
              ? 'bg-[#FF671F]/10 text-[#FF671F] hover:bg-[#FF671F]/20'
              : isDark
              ? 'bg-blue-600/20 text-blue-400 hover:bg-blue-600/30'
              : 'bg-blue-50 text-blue-700 hover:bg-blue-100'
          }`}
          title={
            isRecording
              ? (lang === 'en' ? 'Stop Listening' : 'सुनना बंद करें')
              : (lang === 'en' ? 'Voice Assist (Speak now)' : 'आवाज़ से पूछें')
          }
        >
          {isRecording ? <Square className="w-3.5 h-3.5 fill-current" /> : <Mic className="w-4 h-4" />}
        </button>

        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleUserQuery(inputVal);
          }}
          placeholder={
            isRecording
              ? (lang === 'en' ? 'Listening... Speak now...' : 'सुन रहे हैं... कृपया बोलें...')
              : t.voicePromptPlaceholder
          }
          className={`flex-1 h-9 bg-transparent text-xs outline-none px-1 ${
            isDark
              ? 'text-white placeholder:text-slate-500'
              : 'text-slate-900 placeholder:text-slate-400'
          }`}
        />

        <button
          onClick={() => handleUserQuery(inputVal)}
          disabled={!inputVal.trim()}
          className={`w-9 h-9 rounded-xl text-white disabled:opacity-40 transition-colors shrink-0 inline-flex items-center justify-center ${
            isTiranga
              ? 'bg-[#FF671F] hover:bg-[#E65100]'
              : 'bg-blue-600 hover:bg-blue-500'
          }`}
          title="Send"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
