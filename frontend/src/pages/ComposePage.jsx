import Layout from "../components/Layout";
import NeomorphCard from "../components/NeomorphCard";
import JDComposerEditor from "../components/JDComposerEditor";
import AIPromptsSidebar from "../components/AIPromptsSidebar";
import PreviewPanel from "../components/PreviewPanel";

export default function ComposePage(){
  return (
    <Layout>
      <div className="grid lg:grid-cols-[1.2fr,.9fr] gap-6">
        <NeomorphCard className="p-0 overflow-hidden">
          <JDComposerEditor/>
        </NeomorphCard>
        <div className="grid gap-6">
          <NeomorphCard><AIPromptsSidebar/></NeomorphCard>
          <NeomorphCard><PreviewPanel/></NeomorphCard>
        </div>
      </div>
    </Layout>
  );
}