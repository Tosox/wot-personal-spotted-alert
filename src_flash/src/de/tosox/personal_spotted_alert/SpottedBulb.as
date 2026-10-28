package de.tosox.personal_spotted_alert
{
   import flash.display.DisplayObject;
   import flash.display.DisplayObjectContainer;
   import flash.display.MovieClip;
   import flash.display.Sprite;
   import flash.events.Event;
   import flash.geom.Point;
   import flash.geom.Rectangle;
   import flash.utils.getDefinitionByName;
   import flash.utils.getQualifiedClassName;

   // Inserted into a VehicleMarker through its vanilla insertSymbol and driven
   // from Python through callInsertedSymbolMethod. It wraps the vanilla target
   // designator bulb and pins it to the left of the marker's health bar
   public class SpottedBulb extends Sprite
   {
      // Lives in battleVehicleMarkers.swf, which the markers movie always loads
      private static const BULB_CLASS:String = "VehicleTargetDesignatorUI";

      // Markers created by XVM, whose health bar is its own (see getXvmBarBounds)
      private static const XVM_MARKER_CLASS:String = "XvmVehicleMarker";

      private static const SPRITE_CLASS:String = "flash.display::Sprite";
      private static const MOVIE_CLIP_CLASS:String = "flash.display::MovieClip";

      private var _bulb:MovieClip = null;
      private var _layoutY:Number = 0;
      private var _offsetX:Number = 0;
      private var _offsetY:Number = 0;
      private var _anchoring:Boolean = false;

      public function SpottedBulb()
      {
         super();
         mouseEnabled = false;
         mouseChildren = false;
         var bulbClass:Class = getDefinitionByName(BULB_CLASS) as Class;
         this._bulb = new bulbClass() as MovieClip;
         // Without the frame scripts the hide animation loops back into view
         Object(this._bulb).setupFrameEvents();
         addChild(this._bulb);
         addEventListener(Event.REMOVED_FROM_STAGE, this.onRemovedFromStageHandler);
      }

      // The marker stacks its parts by height and y. Reporting no height and
      // keeping the stack's y apart from our own leaves its layout untouched
      override public function get height() : Number
      {
         return 0;
      }

      override public function get y() : Number
      {
         return this._layoutY;
      }

      override public function set y(value:Number) : void
      {
         this._layoutY = value;
      }

      // Offset of the bulb's centre from the anchor's left edge and vertical centre
      public function setLayout(offsetX:Number, offsetY:Number, scale:Number) : void
      {
         this._offsetX = offsetX;
         this._offsetY = offsetY;
         this._bulb.scaleX = this._bulb.scaleY = scale;
         this.updatePosition();
      }

      public function setColor(colorName:String, rgb:uint) : void
      {
         Object(this._bulb).setEffectColor(colorName, rgb);
      }

      public function show() : void
      {
         // No countdown, not a one-shot, play the show animation
         Object(this._bulb).showEffectTimer(0, false, false, true);
         this.startAnchoring();
      }

      public function hide() : void
      {
         Object(this._bulb).hideEffectTimer(true);
      }

      public function dispose() : void
      {
         this.stopAnchoring();
         removeEventListener(Event.REMOVED_FROM_STAGE, this.onRemovedFromStageHandler);
         if(this._bulb != null)
         {
            Object(this._bulb).dispose();
            removeChild(this._bulb);
            this._bulb = null;
         }
      }

      // The health bar moves when the player toggles the extended marker info,
      // so follow it every frame for as long as the bulb is on screen
      private function startAnchoring() : void
      {
         this.updatePosition();
         if(!this._anchoring)
         {
            this._anchoring = true;
            addEventListener(Event.ENTER_FRAME, this.onEnterFrameHandler);
         }
      }

      private function stopAnchoring() : void
      {
         if(this._anchoring)
         {
            this._anchoring = false;
            removeEventListener(Event.ENTER_FRAME, this.onEnterFrameHandler);
         }
      }

      private function updatePosition() : void
      {
         var bounds:Rectangle = this.findAnchorBounds();
         if(bounds == null)
         {
            return;
         }
         super.x = bounds.left + this._offsetX;
         super.y = bounds.top + bounds.height / 2 + this._offsetY;
      }

      // What the bulb sits next to, in the marker's coordinates, in order of
      // preference; each step covers a marker the ones before don't
      private function findAnchorBounds() : Rectangle
      {
         if(parent == null)
         {
            return null;
         }
         var bounds:Rectangle = this.getVanillaBarBounds();
         if(bounds == null)
         {
            bounds = this.getXvmBarBounds();
         }
         if(bounds == null)
         {
            // The vanilla health bar can be switched off in the marker settings
            var hpField:DisplayObject = this.getMarkerMember("hpField");
            if(hpField != null && hpField.visible)
            {
               bounds = hpField.getBounds(parent);
            }
         }
         return bounds;
      }

      // The health bar's own bounds also cover its hit splash and shine/glitch
      // effects, which come and go, so they would drag the bulb around. Its bar
      // always starts at local x 0, and only the bar clip itself is measured
      private function getVanillaBarBounds() : Rectangle
      {
         var anchor:DisplayObject = this.getMarkerMember("healthBar");
         if(anchor == null || !anchor.visible)
         {
            return null;
         }
         var bar:DisplayObject = null;
         try
         {
            bar = Object(anchor).healthBar as DisplayObject;
         }
         catch(e:Error)
         {
            bar = null;
         }
         if(bar == null)
         {
            return anchor.getBounds(parent);
         }
         var bounds:Rectangle = bar.getBounds(parent);
         bounds.left = parent.globalToLocal(anchor.localToGlobal(new Point(0, 0))).x;
         return bounds;
      }

      // XVM's markers hide the vanilla bar and draw their own: an unnamed Sprite
      // on the marker holding its border, fill and damage clips, in that order
      private function getXvmBarBounds() : Rectangle
      {
         if(getQualifiedClassName(parent).indexOf(XVM_MARKER_CLASS) == -1)
         {
            return null;
         }
         var n:int = parent.numChildren;
         for(var i:int = 0; i < n; ++i)
         {
            var bar:DisplayObjectContainer = parent.getChildAt(i) as DisplayObjectContainer;
            if(bar == null || bar == this || !bar.visible || !isXvmHealthBar(bar))
            {
               continue;
            }
            // The damage clip animates on hits, so only border and fill count
            var bounds:Rectangle = bar.getChildAt(0).getBounds(parent).union(bar.getChildAt(1).getBounds(parent));
            return bounds.isEmpty() ? null : bounds;
         }
         return null;
      }

      private static function isXvmHealthBar(bar:DisplayObjectContainer) : Boolean
      {
         return bar.numChildren == 3
            && getQualifiedClassName(bar) == SPRITE_CLASS
            && getQualifiedClassName(bar.getChildAt(0)) == SPRITE_CLASS
            && getQualifiedClassName(bar.getChildAt(1)) == SPRITE_CLASS
            && getQualifiedClassName(bar.getChildAt(2)) == MOVIE_CLIP_CLASS;
      }

      private function getMarkerMember(name:String) : DisplayObject
      {
         try
         {
            return parent[name] as DisplayObject;
         }
         catch(e:Error)
         {
         }
         return null;
      }

      private function onEnterFrameHandler(event:Event) : void
      {
         // The bulb hides itself once its hide animation has played out
         if(this._bulb == null || !this._bulb.visible)
         {
            this.stopAnchoring();
            return;
         }
         this.updatePosition();
      }

      // A marker disposes its inserted parts without calling dispose on them
      private function onRemovedFromStageHandler(event:Event) : void
      {
         this.stopAnchoring();
      }
   }
}
