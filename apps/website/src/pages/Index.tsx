import Hero from "@/components/landing/Hero";
import Navbar from "@/components/layout/Navbar";
import Highlights from "@/components/landing/Highlights";
import Overview from "@/components/landing/Overview";
import DigitalOutputs from "@/components/landing/DigitalOutputs";
import InputsSensing from "@/components/landing/InputsSensing";
import FirmwareRuntime from "@/components/landing/FirmwareRuntime";
import CommInterfaces from "@/components/landing/CommInterfaces";
import PowerSupply from "@/components/landing/PowerSupply";
import Microcontroller from "@/components/landing/Microcontroller";
import SystemArchitecture from "@/components/landing/SystemArchitecture";
import HMIPanel from "@/components/landing/HMIPanel";
import CloudRemote from "@/components/landing/CloudRemote";
import Features from "@/components/landing/Features";
import Applications from "@/components/landing/Applications";
import Specs from "@/components/landing/Specs";
import IOSummary from "@/components/landing/IOSummary";
import NoteBox from "@/components/landing/NoteBox";
import BoardBaseAssembly from "@/components/landing/BoardBaseAssembly";
import Footer from "@/components/landing/Footer";
import { useFeatureFlags } from "@/hooks/useFeatureFlags";

const Index = () => {
  const { isEnabled } = useFeatureFlags();

  return (
    <div className="min-h-screen bg-background">
      <Hero />
      <Navbar />
      <Highlights />
      <Overview />
      <DigitalOutputs />
      <InputsSensing />
      <FirmwareRuntime />
      <CommInterfaces />
      <PowerSupply />
      {isEnabled("mcu") && <Microcontroller />}
      <SystemArchitecture />
      <HMIPanel />
      {isEnabled("cloud") && <CloudRemote />}
      <Features />
      <Applications />
      <Specs />
      <IOSummary />
      {isEnabled("dsrev") && <NoteBox />}
      {isEnabled("assembly") && <BoardBaseAssembly />}
      <Footer />
    </div>
  );
};

export default Index;
