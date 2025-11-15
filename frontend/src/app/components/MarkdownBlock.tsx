/* eslint-disable prefer-const */
/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { visit } from 'unist-util-visit';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { Root } from "hast";
import remarkGfm from "remark-gfm";
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
// import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import rehypeRaw from 'rehype-raw';
import styles from './ChatMessage.module.scss';

interface ChatBlockProps {
  markdown: string;
  role?: string;
}

function rehypeInlineCodeProperty() {
  return function (tree: Root): void {
    visit(tree, 'element', (node, index, parent) => {
      if (node.tagName === 'code') {
        const isInline = node.position && node.position.start.line === node.position.end.line;
        node.properties.dataInline = isInline;
      }
    });
  };
}



const MarkdownBlock: React.FC<ChatBlockProps> = ({ markdown }) => {
 
  // Replace \[ with $$ and \] with $$ to ensure compatibility
  const processedText = markdown
    ?.replace(/\\\[/g, '$$$')  // Replace all occurrences of \[ with $$
    ?.replace(/\\\]/g, '$$$') // Replace all occurrences of \] with $$
    ?.replace(/\\\(/g, '$$$')  // Replace all occurrences of \( with $$
    ?.replace(/\\\)/g, '$$$'); // Replace all occurrences of \) with $$
  
  // const processedText = markdown
    // ?.replace(/\\\[/g, '$$')  // Display math: \[...\] -> $$...$$
    // ?.replace(/\\\]/g, '$$') 
    // ?.replace(/\\\(/g, '$')   // Inline math: \(...\) -> $...$
    // ?.replace(/\\\)/g, '$');

  const remarkMathOptions = {
    singleDollarTextMath: false,
  };

  function inlineCodeBlock({ value, language }: { value: string; language: string | undefined }) {
    return (
      <code style={{background: '#e1e1e1', padding: '0 5px'}}>
        {value}
      </code>
    );
  }

  // Function to extract text content from table for copying
  function extractTableText(children: any): string {
    const extractTextFromNode = (node: any): string => {
      if (typeof node === 'string') {
        return node.trim();
      }
      if (typeof node === 'number') {
        return node.toString();
      }
      if (Array.isArray(node)) {
        return node.map(extractTextFromNode).filter(text => text).join(' ');
      }
      if (React.isValidElement(node) && node.props && typeof node.props === 'object' && 'children' in node.props) {
        return extractTextFromNode((node.props as any).children);
      }
      return '';
    };

    const processTableSection = (section: any): string[] => {
      if (!section || !section.props || !section.props.children) {
        return [];
      }

      const rows = Array.isArray(section.props.children) 
        ? section.props.children 
        : [section.props.children];

      return rows.map((row: any) => {
        if (!row || !row.props || !row.props.children) {
          return '';
        }

        const cells = Array.isArray(row.props.children) 
          ? row.props.children 
          : [row.props.children];

        return cells
          .map((cell: any) => extractTextFromNode(cell))
          .filter((text: string) => text !== '')
          .join('\t');
      }).filter((row: string) => row !== '');
    };

    if (!children) {
      return '';
    }

    const sections = Array.isArray(children) ? children : [children];
    const allRows: string[] = [];

    sections.forEach((section: any) => {
      const sectionRows = processTableSection(section);
      allRows.push(...sectionRows);
    });

    return allRows.join('\n');
  }

  function tableBlock({ children, ...props }: any) {
    const tableText = extractTableText(children);
    
    return (
      <div className="border border-gray-200 rounded-md bg-gray-50 mb-2">
        <div className="flex items-center relative text-black bg-gray-100 px-4 py-1.5 text-xs font-sans justify-between rounded-t-md">
          <span>Table</span>
          {/* <CopyButton text={tableText} /> */}
        </div>
        <div className="p-4 overflow-auto">
          <table {...props}>{children}</table>
        </div>
      </div>
    );
  }

  function linkRenderer({ href, children, ...props }: any) {
    return (
      <a 
        href={href} 
        target="_blank" 
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    );
  }

  function codeBlock({ node, className, children, ...props }: any) {
    if (!children) {
      return null;
    }
    const value = String(children).replace(/\n$/, '');
    if (!value) {
      return null;
    }
    // Note: OpenAI does not always annotate the Markdown code block with the language
    // Note: In this case, we will fall back to plaintext
    const match = /language-(\w+)/.exec(className || '');
    const language: string = match ? match[1] : 'plaintext';
    const isInline = node.properties.dataInline;

    return (isInline || language === 'plaintext') ? (
      inlineCodeBlock({ value: value, language })
    ) : (
      <div className="border border-gray-200 rounded-md bg-gray-200 codeBlockContainer mb-2">
        <div
          className="flex items-center relative text-black bg-gray-850 px-4 py-1.5 text-xs font-sans justify-between rounded-t-md">
          <span>{language}</span>
          {/* <CopyButton text={children} /> */}
        </div>
        <div className="overflow-y-auto">
          <SyntaxHighlighter
            language={language}
            style={oneLight}
            customStyle={{ margin: '0' }}
          >
            {value}
          </SyntaxHighlighter>
          {/* <code {...props} className={className}>
                        {children}
                    </code>*/}
        </div>
      </div>
    );
  }

  const renderers = {
    code: codeBlock,
    table: tableBlock,
    a: linkRenderer,
    // p: textRenderer,
    // span: textRenderer,
    // h1: textRenderer,
    // h2: textRenderer,
    // h3: textRenderer,
    // h4: textRenderer,
    // h5: textRenderer,
  };

  return (
    <div>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, [remarkMath, remarkMathOptions]]}
        components={renderers}
        rehypePlugins={[rehypeKatex, rehypeInlineCodeProperty, rehypeRaw]}
      >
        {processedText}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownBlock;
